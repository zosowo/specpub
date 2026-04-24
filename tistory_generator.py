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

_PROMPT = """당신은 한국어 블로그 SEO 카피라이터입니다. 다음 핫 키워드를 기반으로 티스토리 블로그 글을 작성합니다.

## 입력
- 핵심 키워드: {keyword}
- 연관 키워드: {related}
- 카테고리: {category}

## 출력 요건
**반드시 아래 JSON 객체 하나만** 출력하세요. 앞뒤 설명·마크다운 펜스(```) 금지.

{{
  "title": "한국어 제목 (25~45자, 숫자나 연도 포함, 호기심 유발, 클릭 유도)",
  "body_html": "본문 HTML (800~1200자 한국어)",
  "tags": ["태그1","태그2","..."],
  "image_query": "pixabay용 영어 검색어 (1~3 단어)"
}}

## body_html 작성 규칙
- 순수 HTML (<article> 생략, <h2> 부터 시작). ```html 마크다운 블록 금지.
- 구조: 도입 <p> (2~3문장) → <h2> 3~4개 → 마무리 <p>
- 연관 키워드를 본문에 **자연스럽게 2~3개** 삽입 (SEO)
- 리스트 (<ul> 또는 <ol>) 1개 포함
- 한국 독자 관점에서 유용한 팁·맥락·수치 포함
- **광고성 표현·쿠팡/제휴 링크·과장 추천·투기성 예측 금지**
- **확인 불가능한 루머·가십·정치·선수 성적·사건사고 언급 금지**

## tags 규칙
- 5~8개 한국어 태그
- 핵심 키워드 + 연관 키워드 일부 + 카테고리 관련 일반 태그

## image_query
- Pixabay 영어 검색어 (예: "smartphone unboxing", "travel beach", "electric car")
- 한국 고유명사는 일반 영어 단어로 (예: "갤럭시 S26" → "smartphone")
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
            capture_output=True, text=True, timeout=150,
        )
    except Exception as e:
        log.warning(f'[claude] 호출 실패 ({keyword}): {e}')
        return {}

    raw = (result.stdout or '').strip()
    m = re.search(r'\{[\s\S]*\}', raw)
    if not m:
        log.warning(f'[claude] JSON 없음 ({keyword}): {raw[:200]}')
        return {}
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        log.warning(f'[claude] JSON 파싱 실패 ({keyword}): {e}')
        return {}

    # 필드 정규화
    return {
        'title':       str(obj.get('title', '')).strip(),
        'body_html':   str(obj.get('body_html', '')).strip(),
        'tags':        [str(t).strip() for t in (obj.get('tags') or []) if t],
        'image_query': str(obj.get('image_query', '')).strip(),
    }


# ──────────────────────────────────────────────────────────
# Pixabay (간단 쿼리 기반) + F단계 비전 게이트
# ──────────────────────────────────────────────────────────

def fetch_image_url(query: str, topic: str) -> str:
    """Pixabay 에서 query 검색 → 비전 게이트 통과한 첫 URL 반환. 실패시 ''."""
    if not query:
        return ''
    try:
        r = requests.get(
            'https://pixabay.com/api/',
            params={
                'key':         PIXABAY_KEY,
                'q':           query,
                'image_type':  'photo',
                'orientation': 'horizontal',
                'per_page':    15,
                'safesearch':  'true',
            },
            headers={'User-Agent': _UA},
            timeout=10,
        )
        hits = r.json().get('hits', [])
    except Exception as e:
        log.warning(f'[pixabay] 실패 ({query}): {e}')
        return ''

    for hit in hits[:8]:
        url = hit.get('webformatURL', '') or hit.get('largeImageURL', '')
        if not url:
            continue
        try:
            if cg.check_image_fits(url, topic):
                return url
        except Exception as e:
            log.warning(f'[vision] 오류 → fail-open: {e}')
            return url
    return ''


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

        # 이미지 소싱
        img_url = fetch_image_url(out['image_query'], out['title'])
        if img_url:
            alt = out['title']
            img_tag = f'<p><img src="{img_url}" alt="{alt}" loading="lazy"></p>'
            body = img_tag + out['body_html']
        else:
            log.info(f'[gen] 이미지 미채택 — 본문만 발행: {kw}')
            body = out['body_html']

        entry = {
            'title':      out['title'],
            'html_body':  body,
            'tags':       out['tags'][:8],
            'keyword':    kw,
            'category':   category,
            'image_url':  img_url,
            'created_at': datetime.now(KST).isoformat(timespec='seconds'),
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
