"""
트렌드 자동 포스팅 파이프라인 — 매일 02:00.

1. victor-jk AutoNewsItem DB에서 최근 24h IT 기사 조회
2. Claude로 전자기기·IT 트렌드 주제 N개 추출 (단일 기업 사건 제외)
3. 각 주제 본문 생성 + 검증
4. 큐에 type='trend'로 저장 → publish_next.py가 기존 발행 스케줄에서 소비

크론: 0 2 * * * TZ=Asia/Seoul /usr/bin/python3 /home/zosowo/specpub/trend_generator.py
      >> /home/zosowo/specpub/trend.log 2>&1
"""
import os
import json
import logging
import re
import subprocess
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

import psycopg2

import content_generator as cg
import queue_manager as qm
import telegram_utils as tg

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

TREND_PER_DAY = int(os.getenv('TREND_PER_DAY', '2'))
DB_URL        = os.getenv('VICTOR_JK_DB_URL')


def fetch_recent_articles(hours: int = 24) -> list:
    if not DB_URL:
        log.error('VICTOR_JK_DB_URL 미설정')
        return []
    try:
        since = datetime.now() - timedelta(hours=hours)
        conn = psycopg2.connect(DB_URL)
        cur  = conn.cursor()
        cur.execute(
            'SELECT title, summary FROM "AutoNewsItem" '
            'WHERE "publishedAt" >= %s ORDER BY "publishedAt" DESC LIMIT 300',
            (since,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [(t, s or '') for t, s in rows]
    except Exception as e:
        log.error(f'DB 조회 실패: {e}')
        return []


def extract_topics(articles: list, n: int) -> list:
    """Claude로 트렌드 주제 n개 추출 (JSON 배열 반환)."""
    if not articles:
        return []

    sample   = articles[:80]
    bulleted = '\n'.join(f'- {t} :: {(s or "")[:120]}' for t, s in sample)

    prompt = f"""다음은 최근 24시간 IT·전자기기 관련 뉴스 제목과 요약입니다.
이 중에서 한국 독자에게 유용한 **전자기기/IT 기술 트렌드 블로그 주제** {n}개를 골라주세요.

규칙:
- 단일 기업의 실적·인사·법원 판결 등은 제외
- 제품/기술/소비자 관심사 관련 거시 흐름만 채택 (예: 이어폰 AI 통역 확산, 폴더블 내구성 개선, 스마트홈 Matter 채택 가속)
- 주제는 구체적이고 검색 가능한 형태
- 서로 다른 카테고리·기술 영역의 주제로 다양화
- 반드시 아래 JSON 배열 형식으로만 응답 (주석·설명 없이):

[
  {{"title": "주제1 제목", "context": "1~2문장 컨텍스트"}},
  {{"title": "주제2 제목", "context": "..."}}
]

뉴스 목록:
{bulleted}
"""

    try:
        result = subprocess.run(
            [cg.CLAUDE_BIN, '--model', cg.MODEL, '-p', prompt],
            capture_output=True, text=True, timeout=120,
        )
        out = result.stdout.strip()
        m = re.search(r'\[.*\]', out, re.DOTALL)
        if not m:
            log.warning(f'Claude 응답에 JSON 배열 없음: {out[:200]}')
            return []
        topics = json.loads(m.group())
        return topics[:n] if isinstance(topics, list) else []
    except json.JSONDecodeError as e:
        log.error(f'JSON 파싱 실패: {e}')
        return []
    except Exception as e:
        log.error(f'Claude 트렌드 추출 실패: {e}')
        return []


def make_slug(title: str) -> str:
    """한글 포함 제목을 안전한 slug로 변환. 날짜 prefix로 중복 방지."""
    base = re.sub(r'[^\w가-힣]+', '-', title.lower()).strip('-')
    base = base[:40] or 'topic'
    return f'trend-{date.today().isoformat()}-{base}'


def next_queue_index(date_str: str) -> int:
    d = os.path.join(qm.QUEUE_DIR, date_str)
    if not os.path.isdir(d):
        return 1
    files = [f for f in os.listdir(d) if f.endswith('.json')]
    return len(files) + 1


def run(date_str: str, n: int = TREND_PER_DAY):
    articles = fetch_recent_articles(24)
    log.info(f'최근 24h 기사: {len(articles)}건')

    topics = extract_topics(articles, n)
    log.info(f'추출된 트렌드 주제: {len(topics)}개')
    for t in topics:
        log.info(f'  • {t.get("title", "(제목없음)")}')

    published = qm.load_published()
    queued    = qm.get_queued_slugs()
    saved     = 0
    start_idx = next_queue_index(date_str)

    for topic in topics:
        title = (topic.get('title') or '').strip()
        if not title:
            continue
        slug = make_slug(title)
        if slug in published or slug in queued:
            log.info(f'이미 존재: {slug}')
            continue

        log.info(f'[트렌드] 본문 생성: {title}')
        try:
            html = cg.generate_trend_post(topic)
            ok, reason = cg.verify_trend_content(html)
            if not ok:
                log.warning(f'  검증 실패: {reason} — 재시도')
                html = cg.generate_trend_post(topic)
                ok, reason = cg.verify_trend_content(html)
            if not ok:
                log.error(f'  재시도 실패: {reason} — 건너뜀')
                continue
        except Exception as e:
            log.error(f'  오류: {e}')
            continue

        qm.save_to_queue({
            'type':         'trend',
            'slug':         slug,
            'title':        title,
            'content_html': html,
            'product':      None,
        }, date_str, start_idx + saved)
        saved += 1
        log.info(f'  ✓ 큐 저장: {slug}')

    tg.record_stats('trend', {
        'articles': len(articles),
        'topics':   len(topics),
        'saved':    saved,
    })

    if saved == 0:
        tg.send(
            f'⚠️ *[스펙분석소] trend_generator 경고*\n'
            f'오늘 트렌드 큐 저장 0개 '
            f'(기사 {len(articles)}건, 주제 {len(topics)}개)'
        )

    log.info(f'완료: {saved}개 저장')
    return saved


if __name__ == '__main__':
    run(date.today().isoformat())
