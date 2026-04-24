"""
트렌드 자동 포스팅 — 매일 02:00.

외부 소스(Google News RSS 한국 IT) **우선** + victor-jk DB 보조.
Claude로 핫 트렌드 주제·키워드 추출 → `keyword_history.json`에 점수 누적.
점수 ≥ HOT_THRESHOLD 인 키워드는 `is_hot=True` 로 큐잉 → publish_next.py 가
'인기' 태그 + sticky 고정 적용.

쿨다운 (KEYWORD_COOLDOWN_DAYS): 같은 키워드 중 하나라도 최근 발행 이력 있으면 건너뜀.
일일 점수 감쇠: 오늘 등장 안 한 키워드는 score -1.

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

import feedparser
import psycopg2

import content_generator as cg
import queue_manager as qm
import telegram_utils as tg
import trend_sources as ts

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# ── 설정 ──
TREND_PER_DAY    = int(os.getenv('TREND_PER_DAY',                 '2'))
HOT_THRESHOLD    = int(os.getenv('TREND_HOT_THRESHOLD',           '5'))
PIN_DAYS         = int(os.getenv('TREND_PIN_DAYS',                '7'))
KEYWORD_COOLDOWN = int(os.getenv('TREND_KEYWORD_COOLDOWN_DAYS', '14'))

BASE_DIR  = os.path.dirname(__file__)
KW_HIST_F = os.path.join(BASE_DIR, 'keyword_history.json')

# Google News RSS 검색 쿼리 (한국어, 최근 순) — 전자기기/IT 중심
GOOGLE_NEWS_URLS = [
    'https://news.google.com/rss/search?q=IT+%EC%A0%84%EC%9E%90%EC%A0%9C%ED%92%88&hl=ko-KR&gl=KR&ceid=KR:ko',
    'https://news.google.com/rss/search?q=%EC%8A%A4%EB%A7%88%ED%8A%B8%ED%8F%B0+%EB%85%B8%ED%8A%B8%EB%B6%81&hl=ko-KR&gl=KR&ceid=KR:ko',
    'https://news.google.com/rss/search?q=%EC%9D%B4%EC%96%B4%ED%8F%B0+%EC%8A%A4%EB%A7%88%ED%8A%B8%EC%9B%8C%EC%B9%98&hl=ko-KR&gl=KR&ceid=KR:ko',
    'https://news.google.com/rss/search?q=%ED%8C%8C%EA%B5%AC%EB%9D%BC%EB%8B%88+%EB%B0%98%EB%8F%84%EC%B2%B4+AI&hl=ko-KR&gl=KR&ceid=KR:ko',
]

DB_URL = os.getenv('VICTOR_JK_DB_URL')


# ──────────────────────────────────────────────────────────
# 소스 수집
# ──────────────────────────────────────────────────────────

def fetch_google_news() -> list:
    """Google News RSS (한국 IT). 반환: [(title, summary, 'google_news'), ...]"""
    articles = []
    for url in GOOGLE_NEWS_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:30]:
                title   = getattr(entry, 'title', '').strip()
                summary = getattr(entry, 'summary', '') or ''
                summary = re.sub(r'<[^>]+>', ' ', summary).strip()[:200]
                if title:
                    articles.append((title, summary, 'google_news'))
        except Exception as e:
            log.warning(f'Google News 실패: {url[:60]}... — {e}')
    # 제목 중복 제거
    seen = set()
    out  = []
    for t, s, src in articles:
        if t in seen:
            continue
        seen.add(t)
        out.append((t, s, src))
    return out


def fetch_victor_jk() -> list:
    """victor-jk AutoNewsItem DB 보조 소스."""
    if not DB_URL:
        return []
    try:
        since = datetime.now() - timedelta(hours=24)
        conn  = psycopg2.connect(DB_URL)
        cur   = conn.cursor()
        cur.execute(
            'SELECT title, summary FROM "AutoNewsItem" '
            'WHERE "publishedAt" >= %s ORDER BY "publishedAt" DESC LIMIT 200',
            (since,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [(t, s or '', 'victor_jk') for t, s in rows]
    except Exception as e:
        log.error(f'victor-jk DB 조회 실패: {e}')
        return []


def fetch_external_trends() -> list:
    """pytrends(Google Trends 한국 일간) + YouTube Data API 인기 영상.
    반환: [(title, summary, 'google_trends'|'youtube'), ...]"""
    items = ts.collect_external_keywords(limit_per_source=20)
    out   = []
    for it in items:
        kw  = it['keyword']
        ctx = it.get('context', '')
        out.append((kw, ctx, it['source']))
    return out


def fetch_all() -> list:
    """외부 트렌드(Google Trends + YouTube) **최우선** → Google News RSS → victor-jk 보조."""
    ext_trend = fetch_external_trends()
    log.info(f'외부 트렌드(Google Trends/YouTube): {len(ext_trend)}건')
    news = fetch_google_news()
    log.info(f'Google News RSS: {len(news)}건')
    vjk = fetch_victor_jk()
    log.info(f'victor-jk DB: {len(vjk)}건')
    # 순서: 외부 트렌드 키워드 → Google News → victor-jk
    # Claude 입력에서 앞쪽에 더 자주 노출되므로 프롬프트 가중치 역할
    return ext_trend + news + vjk


# ──────────────────────────────────────────────────────────
# 키워드 히스토리
# ──────────────────────────────────────────────────────────

def _normalize(kw: str) -> str:
    return re.sub(r'\s+', ' ', (kw or '').strip().lower())


def load_history() -> dict:
    if not os.path.exists(KW_HIST_F):
        return {}
    try:
        with open(KW_HIST_F, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log.warning(f'keyword_history 로드 실패: {e}')
        return {}


def save_history(h: dict):
    tmp = KW_HIST_F + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(h, f, ensure_ascii=False, indent=2)
    os.replace(tmp, KW_HIST_F)


def decay_history(h: dict, today: str):
    """오늘 등장 없는 키워드는 score -1."""
    for info in h.values():
        if info.get('last_seen') != today and info.get('score', 0) > 0:
            info['score'] = info['score'] - 1


def has_recent_publish(keywords_norm, history, cooldown_days: int) -> bool:
    """쿨다운 내 이미 동일 키워드로 발행한 이력 있으면 True."""
    cutoff = (datetime.now() - timedelta(days=cooldown_days)).date().isoformat()
    for kw in keywords_norm:
        info = history.get(kw, {}) or {}
        pub_at = info.get('published_at')
        if info.get('published_slug') and pub_at and pub_at >= cutoff:
            return True
    return False


def update_scores(topics: list, history: dict, today: str):
    """토픽별 키워드를 history에 누적 + topic에 score·is_hot 부여."""
    for topic in topics:
        raw_kws = topic.get('keywords') or []
        kws     = [_normalize(k) for k in raw_kws if k]
        topic_score = 0
        for kw in kws:
            if kw not in history:
                history[kw] = {
                    'first_seen':  today,
                    'last_seen':   today,
                    'score':       1,
                    'occurrences': [today],
                }
            else:
                info = history[kw]
                if info.get('last_seen') != today:
                    info['score']     = info.get('score', 0) + 1
                    info['last_seen'] = today
                    info.setdefault('occurrences', []).append(today)
            topic_score = max(topic_score, history[kw]['score'])
        topic['keywords_n'] = kws
        topic['score']      = topic_score
        topic['is_hot']     = topic_score >= HOT_THRESHOLD


# ──────────────────────────────────────────────────────────
# Claude 주제 추출
# ──────────────────────────────────────────────────────────

def extract_topics(articles: list, n_candidates: int) -> list:
    if not articles:
        return []
    sample   = articles[:100]
    bulleted = '\n'.join(f'- [{src}] {t} :: {(s or "")[:120]}' for t, s, src in sample)

    prompt = f"""다음은 오늘 한국 IT/전자기기 관련 뉴스 목록입니다. 가장 핫한 트렌드 주제 {n_candidates}개를 뽑아주세요.

규칙:
- **[google_trends], [youtube] 소스의 항목은 지금 검색·시청이 가장 뜨거운 키워드**이므로 최우선으로 반영
- google_news 는 뉴스 맥락 보강용, victor_jk 는 국내 뉴스 보조용
- 단일 기업 실적·인사·법원 판결·단순 제품 발표는 제외
- 기술 흐름, 소비자 관심, 제품 카테고리 변화 같은 거시 트렌드만
- 각 주제에 "keywords" 배열(2~4개 핵심어, 한국어 명사구 위주) 포함 — 나중에 중복/우선순위 판단용
- 서로 다른 주제끼리 keywords가 겹치지 않도록 다양화
- title 은 "현재 상황 + 인사이트"가 드러나도록 구성 (예: "갤럭시 Z폴드7 사전 예약 폭주, 폴더블 시장의 분기점이 된 이유")
- JSON 배열로만 응답 (주석·설명 금지):

[
  {{
    "title": "주제 제목 (블로그 포스트 제목으로 쓸 수 있는 형태)",
    "context": "1~2문장 요약",
    "keywords": ["핵심어1", "핵심어2", "핵심어3"]
  }}
]

뉴스:
{bulleted}
"""

    try:
        result = subprocess.run(
            [cg.CLAUDE_BIN, '--model', cg.MODEL, '-p', prompt],
            capture_output=True, text=True, timeout=180,
        )
        out = result.stdout.strip()
        m = re.search(r'\[.*\]', out, re.DOTALL)
        if not m:
            log.warning(f'Claude 응답에 JSON 없음: {out[:200]}')
            return []
        topics = json.loads(m.group())
        return topics[:n_candidates] if isinstance(topics, list) else []
    except json.JSONDecodeError as e:
        log.error(f'JSON 파싱 실패: {e}')
        return []
    except Exception as e:
        log.error(f'Claude 추출 실패: {e}')
        return []


# ──────────────────────────────────────────────────────────
# 큐 저장 보조
# ──────────────────────────────────────────────────────────

def make_slug(title: str) -> str:
    base = re.sub(r'[^\w가-힣]+', '-', (title or '').lower()).strip('-')
    base = base[:40] or 'topic'
    return f'trend-{date.today().isoformat()}-{base}'


def next_queue_index(date_str: str) -> int:
    d = os.path.join(qm.QUEUE_DIR, date_str)
    if not os.path.isdir(d):
        return 1
    return len([f for f in os.listdir(d) if f.endswith('.json')]) + 1


# ──────────────────────────────────────────────────────────
# 실행 본체
# ──────────────────────────────────────────────────────────

def run(date_str: str, n: int = TREND_PER_DAY):
    articles = fetch_all()
    log.info(f'총 수집: {len(articles)}건')

    topics = extract_topics(articles, n_candidates=max(n * 3, 6))
    log.info(f'Claude 추출 주제: {len(topics)}개')

    history = load_history()
    decay_history(history, date_str)
    update_scores(topics, history, date_str)

    # 점수 높은 순으로 정렬
    topics.sort(key=lambda t: t.get('score', 0), reverse=True)

    published = qm.load_published()
    queued    = qm.get_queued_slugs()
    saved     = 0
    start_idx = next_queue_index(date_str)

    for topic in topics:
        if saved >= n:
            break
        title = (topic.get('title') or '').strip()
        if not title:
            continue

        kws = topic.get('keywords_n', [])
        if has_recent_publish(kws, history, KEYWORD_COOLDOWN):
            log.info(f'쿨다운 내 재등장: {title} (kw={kws})')
            continue

        slug = make_slug(title)
        if slug in published or slug in queued:
            log.info(f'이미 존재: {slug}')
            continue

        is_hot = topic.get('is_hot', False)
        log.info(f'[트렌드] 생성: {title} (score={topic.get("score")}, hot={is_hot})')

        try:
            html, hints = cg.generate_trend_post(topic)
            ok, reason = cg.verify_trend_content(html)
            if not ok:
                log.warning(f'  검증 실패: {reason} — 재시도')
                html, hints = cg.generate_trend_post(topic)
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
            'image_hints':  hints,
            'product':      None,
            'keywords':     kws,
            'is_hot':       is_hot,
            'score':        topic.get('score', 0),
        }, date_str, start_idx + saved)

        # 큐잉 단계에서 미리 예약 기록 (재발행 방지)
        for kw in kws:
            history[kw]['published_slug'] = slug
            history[kw]['published_at']   = date_str

        saved += 1
        log.info(f'  ✓ 큐 저장: {slug}')

    save_history(history)

    tg.record_stats('trend', {
        'articles':  len(articles),
        'topics':    len(topics),
        'saved':     saved,
        'hot_count': sum(1 for t in topics[:saved] if t.get('is_hot')),
    })

    if saved == 0:
        tg.send(
            f'⚠️ *[스펙분석소] trend_generator 경고*\n'
            f'오늘 트렌드 큐 저장 0개 (기사 {len(articles)}, 주제 {len(topics)})'
        )

    log.info(f'완료: {saved}개 저장')
    return saved


if __name__ == '__main__':
    run(date.today().isoformat())
