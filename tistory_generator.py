"""
티스토리 큐 빌더 — 매일 새벽 실행.

흐름:
  1. hot_keyword_sources.collect_hot_keywords() 로 6개 핫 키워드 확보.
  2. 각 키워드 → Claude CLI 로 제목+본문+태그+이미지 쿼리 생성.
  3. Pixabay 에서 이미지 조회 + F단계 비전 게이트 통과 시 본문에 <img> 삽입.
  4. 결과를 tistory_queue/{timestamp}_{slug}.json 으로 저장.

JSON 스키마:
  {
    "title":      "한국어 제목",
    "html_body":  "<img>... <h2>... 본문 HTML",
    "tags":       ["태그1", "태그2", ...],
    "keyword":    "seed 핫키워드",
    "category":   "it",
    "created_at": "2026-04-24T03:30:00+09:00"
  }
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv

import hot_keyword_sources as hks
import content_generator as cg

BASE = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE, '.env'))

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

QUEUE_DIR = os.path.join(BASE, 'tistory_queue')
os.makedirs(QUEUE_DIR, exist_ok=True)

TARGET_COUNT  = 6
CLAUDE_MODEL  = 'claude-sonnet-4-6'     # 본문 생성용 (Sonnet 4.6)
CLAUDE_BIN    = cg.CLAUDE_BIN
PIXABAY_KEY   = os.getenv('PIXABAY_API_KEY', '55513176-cde8c9791e54c45fdb2a0cd46')

_UA = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
)

KST = timezone(timedelta(hours=9))


# ──────────────────────────────────────────────────────────
# Claude 본문 생성
# ──────────────────────────────────────────────────────────

_PROMPT = """당신은 한국 개인 블로거입니다. 친근한 톤으로 티스토리 글을 씁니다.
독자가 끝까지 읽고 싶은 재미·정보·공감을 담으세요.

## 입력
- 핵심 키워드: {keyword}
- 연관 키워드: {related}
- 카테고리: {category}

## 출력 (반드시 아래 구분자 형식만. JSON·마크다운 펜스 금지.)

===TITLE===
한국어 제목 (25~45자, 숫자·연도 포함, 호기심 유발, 어그로·과장 금지)

===BODY===
[HTML 본문 — 1000~1200자]

===TAGS===
태그1, 태그2, 태그3, 태그4, 태그5 (한글 5~8개 쉼표 구분)

===IMG===
쿼리1 | 쿼리2 | 쿼리3 (영어 각 1~3단어, 파이프 구분)

===END===

## BODY (HTML) 규칙
- `<h2>` 부터 시작. `<article>` 감쌈 없음. ```html 펜스 없음.
- **폰트 속성 필수**:
  * 모든 `<p>` 에 `data-ke-size="size18"`
  * 모든 `<h2>` 에 `data-ke-size="size26"` (큰 소제목)
  * 모든 `<li>` 에 `data-ke-size="size18"`
- 구조 순서:
  1. 도입 `<p>` 2~3문장 — 독자 공감 훅 (질문·경험·놀라움)
  2. `<h2>` 3~4개, 각 아래 `<p>` 1개 (길게 풀지 말고 핵심만)
  3. 중간에 `<ul>` 리스트 1개 (팁·요약·체크리스트)
  4. 중간에 `<blockquote>` 1개 (핵심 한 줄)
  5. 마지막 `<p>` 는 독자 질문 ("여러분은 어떠세요?")
- **구체 수치·연도·비교 2개 이상 필수** (예: "2025년 대비 2배").
- 연관 키워드 1~2개 자연스럽게 녹이기.
- 톤: "~하더라고요", "~같아요", "저도 최근에" 같은 블로거 말투.
- 강조: 핵심 단어 `<strong>` 로 굵게 (h2당 1~2개).
- 금지: 광고·쿠팡·제휴 언급, 루머·가십·사건사고·정치·스포츠 결과, 과장된 투자 권유.

## IMG 규칙
- 영어 쿼리 3개, 각도 다르게 (예: smartphone → "smartphone unboxing | tech desk | hand holding phone")
- 한국 고유명사는 일반 영어로 치환.
"""


def generate_post_json(keyword: str, related: list[str], category: str) -> dict:
    prompt = _PROMPT.format(
        keyword=keyword,
        related=', '.join(related[:6]) if related else '(없음)',
        category=category,
    )
    try:
        result = subprocess.run(
            [CLAUDE_BIN, '--model', CLAUDE_MODEL, '-p', prompt],
            capture_output=True, text=True, timeout=180,
        )
    except Exception as e:
        log.warning(f'[claude] 호출 실패 ({keyword}): {e}')
        return {}

    raw = (result.stdout or '').strip()
    # 구분자 포맷 파싱 — ===SECTION=== 블록
    def _section(name: str) -> str:
        m = re.search(
            rf'===\s*{name}\s*===\s*(.*?)\s*===\s*(?:TITLE|BODY|TAGS|IMG|END)\s*===',
            raw, re.DOTALL,
        )
        return m.group(1).strip() if m else ''

    title = _section('TITLE')
    body_html = _section('BODY')
    tags_raw = _section('TAGS')
    img_raw = _section('IMG')

    if not title or not body_html:
        log.warning(f'[claude] 섹션 누락 ({keyword[:40]}): '
                    f'title={bool(title)}, body={bool(body_html)}; '
                    f'raw={raw[:200]!r}')
        return {}

    # ```html 펜스가 본문에 있다면 제거
    body_html = re.sub(r'^```(?:html)?\s*|\s*```$', '', body_html).strip()

    tags = [t.strip() for t in re.split(r'[,、]', tags_raw) if t.strip()]
    queries = [q.strip() for q in img_raw.split('|') if q.strip()][:3]

    return {
        'title':         title,
        'body_html':     body_html,
        'tags':          tags,
        'image_queries': queries,
    }


# ──────────────────────────────────────────────────────────
# Pixabay (간단 쿼리 기반) + F단계 비전 게이트
# ──────────────────────────────────────────────────────────

def _pixabay_hits(query: str, per_page: int = 15) -> list[str]:
    """Pixabay 검색 → URL 리스트 (비전 게이트 적용 안 함)."""
    if not query:
        return []
    try:
        r = requests.get(
            'https://pixabay.com/api/',
            params={
                'key':         PIXABAY_KEY,
                'q':           query,
                'image_type':  'photo',
                'orientation': 'horizontal',
                'per_page':    per_page,
                'safesearch':  'true',
            },
            headers={'User-Agent': _UA},
            timeout=10,
        )
        hits = r.json().get('hits', [])
    except Exception as e:
        log.warning(f'[pixabay] 실패 ({query}): {e}')
        return []
    urls = []
    for hit in hits:
        url = hit.get('webformatURL', '') or hit.get('largeImageURL', '')
        if url:
            urls.append(url)
    return urls


def fetch_image_url(query: str, topic: str) -> str:
    """단일 쿼리 → 비전 게이트 통과 첫 URL (레거시/단일 이미지 용)."""
    for url in _pixabay_hits(query)[:8]:
        try:
            if cg.check_image_fits(url, topic):
                return url
        except Exception as e:
            log.warning(f'[vision] 오류 → fail-open: {e}')
            return url
    return ''


def fetch_image_urls(queries: list[str], topic: str, need: int = 3) -> list[str]:
    """쿼리별 Pixabay 후보 → 각 이미지를 Claude 비전 게이트로 적합성 검증.

    사용자 요청(2026-04-25): 3장 모두 글 주제와 어울리는지 Claude 판정.
    건당 ~12s 추가이지만 품질 확보 우선.
    """
    out: list[str] = []
    seen: set[str] = set()
    for q in queries:
        if len(out) >= need:
            break
        for url in _pixabay_hits(q)[:5]:
            if url in seen:
                continue
            seen.add(url)
            try:
                if cg.check_image_fits(url, topic):
                    out.append(url)
                    break
            except Exception as e:
                log.warning(f'[vision] 오류 → fail-open: {e}')
                out.append(url)
                break
    return out


# ──────────────────────────────────────────────────────────
# 시각 스타일 (폰트·자간·행간·여백) — 티스토리 발행 직전 주입
# ──────────────────────────────────────────────────────────

_BODY_STYLE = (
    'font-size:20px; letter-spacing:0.02em; '
    'line-height:1.9; margin-bottom:1.4em;'
)
_H2_STYLE = (
    'font-size:28px; letter-spacing:0.02em; '
    'line-height:1.5; margin-top:1.8em; margin-bottom:0.8em;'
)
_LI_STYLE = (
    'font-size:20px; letter-spacing:0.02em; '
    'line-height:1.9; margin-bottom:0.5em;'
)
_BQ_STYLE = (
    'font-size:20px; letter-spacing:0.02em; line-height:1.8; '
    'margin:1.8em 0; padding:1em 1.2em; border-left:4px solid #888;'
)


def _inject_style(tag: str, html: str, style: str) -> str:
    """특정 태그 모든 인스턴스에 style 속성 추가 (기존 style 있으면 덮어쓰기 않음)."""
    pat = re.compile(rf'<{tag}([^>]*?)>', re.IGNORECASE)
    def _repl(m: re.Match) -> str:
        attrs = m.group(1)
        if re.search(r'\bstyle\s*=', attrs):
            return m.group(0)
        return f'<{tag}{attrs} style="{style}">'
    return pat.sub(_repl, html)


def _polish_html(body_html: str) -> str:
    """글자 크기·자간·행간·여백 인라인 스타일 적용."""
    html = body_html
    html = _inject_style('p',          html, _BODY_STYLE)
    html = _inject_style('h2',         html, _H2_STYLE)
    html = _inject_style('li',         html, _LI_STYLE)
    html = _inject_style('blockquote', html, _BQ_STYLE)
    return html


def _insert_images(body_html: str, image_urls: list[str], alt_text: str) -> str:
    """커버 1장 + 본문 중간 1~2장을 H2 사이에 분산 삽입.

    - urls[0]: 맨 앞 커버
    - urls[1]: 2번째 H2 직전
    - urls[2]: 4번째 H2 직전 (있을 때)
    """
    if not image_urls:
        return body_html

    def _img(url: str) -> str:
        # 이미지 뒤 항상 한 줄 개행(공백 p)로 본문과 간격 확보
        return (
            f'<p data-ke-size="size16" style="text-align:center; margin:1.8em 0 0.6em;">'
            f'<img src="{url}" alt="{alt_text}" loading="lazy" '
            f'style="max-width:100%;height:auto;border-radius:8px;" />'
            f'</p>\n'
            f'<p data-ke-size="size16" style="margin:0 0 1.4em;">&nbsp;</p>\n'
        )

    content = _img(image_urls[0]) + '\n' + body_html
    rest = image_urls[1:3]
    if not rest:
        return content

    # '<h2' 를 경계로 분할. 각 조각이 하나의 H2 섹션이 됨.
    chunks = re.split(r'(?=<h2)', content)
    # chunks[0]: H2 이전 (커버·도입), chunks[1]: 1번째 H2 섹션, chunks[2]: 2번째 H2 섹션, ...

    # 삽입 지점: 2번째 H2 직전(index 2), 4번째 H2 직전(index 4)
    insert_at = [2, 4][:len(rest)]
    for i in reversed(range(len(insert_at))):
        ip = insert_at[i]
        if ip < len(chunks):
            chunks[ip] = _img(rest[i]) + '\n' + chunks[ip]
        else:
            # H2 부족 — 본문 맨 끝에 추가
            chunks.append('\n' + _img(rest[i]))
    return ''.join(chunks)


# ──────────────────────────────────────────────────────────
# 큐 저장
# ──────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    s = re.sub(r'[^A-Za-z0-9가-힣]+', '-', text)
    return s.strip('-')[:40]


def save_to_queue(entry: dict) -> str:
    ts = datetime.now(KST).strftime('%Y%m%d_%H%M%S')
    slug = _slugify(entry['title']) or 'post'
    path = os.path.join(QUEUE_DIR, f'{ts}_{slug}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)
    return path


# ──────────────────────────────────────────────────────────
# 메인
# ──────────────────────────────────────────────────────────

def build_queue(target: int = TARGET_COUNT) -> int:
    picks = hks.collect_hot_keywords(target_count=target)
    if not picks:
        log.error('핫 키워드 확보 실패 — 소스 전부 차단/오류')
        return 0

    saved = 0
    for p in picks:
        kw       = p['keyword']
        related  = p.get('related', []) or []
        category = p.get('category', 'guide')

        log.info(f'[gen] ▶ "{kw}" (cat={category}, related={len(related)})')

        out = generate_post_json(kw, related, category)
        if not out or not out.get('title') or not out.get('body_html'):
            log.warning(f'[gen] 본문 생성 실패 — 스킵: {kw}')
            continue

        # 이미지 소싱 (쿼리 3개 → 최대 3장 수집)
        queries = out.get('image_queries') or []
        if not queries:
            # 폴백: 키워드에서 최소 쿼리 구성
            queries = [kw.split()[0] if kw else 'lifestyle']
        image_urls = fetch_image_urls(queries, out['title'], need=3)
        polished = _polish_html(out['body_html'])
        if image_urls:
            body = _insert_images(polished, image_urls, out['title'])
        else:
            log.info(f'[gen] 이미지 미채택 — 본문만 발행: {kw}')
            body = polished

        entry = {
            'title':        out['title'],
            'html_body':    body,
            'tags':         out['tags'][:8],
            'keyword':      kw,
            'category':     category,
            'image_urls':   image_urls,
            'image_queries': queries,
            'created_at':   datetime.now(KST).isoformat(timespec='seconds'),
        }
        path = save_to_queue(entry)
        saved += 1
        log.info(f'[gen] ✓ 큐 저장 #{saved} → {os.path.basename(path)}')

    log.info(f'[gen] 완료: {saved}/{len(picks)}건 큐 적재 ({QUEUE_DIR})')
    return saved


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--count', type=int, default=TARGET_COUNT,
                    help=f'생성할 큐 개수 (기본 {TARGET_COUNT})')
    args = ap.parse_args()
    n = build_queue(target=args.count)
    sys.exit(0 if n > 0 else 1)
