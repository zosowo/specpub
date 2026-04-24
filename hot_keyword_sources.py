"""
범용 핫 키워드 수집 — 티스토리 이슈 블로그용.

소스:
  • Google Trends Realtime Korea (pytrends)  — 일간 급상승 검색어
  • pytrends related_queries                  — 키워드별 연관·상승 쿼리
  • Google Autocomplete                       — 실시간 자동완성 (연관 확장)
  • YouTube Data API v3                       — 한국 인기 급상승 (카테고리 무관 전체)

카테고리 정책 (애드센스 안전):
  ALLOW  = IT·가전·디지털, 쇼핑·생활, 여행, 영화·드라마 (정보성), 게임, 신제품·세일, 요리·음식,
           자동차, 건강·운동, 재테크·부동산, 팁·가이드
  BLOCK  = 연예인 가십, 정치, 스포츠(경기결과·선수), 사건사고·범죄, 성인·도박, 종교, 논란

필터링은 Claude CLI 분류로 처리 (`classify_keywords_for_tistory`).

반환 포맷:
  [
    {"keyword": "갤럭시 S26 언박싱", "source": "google_trends", "related": ["s26 가격", ...]},
    ...
  ]
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
from urllib.parse import quote

import requests

log = logging.getLogger(__name__)

CLAUDE_BIN = '/home/zosowo/.nvm/versions/node/v24.14.0/bin/claude'
CLAUDE_CLASSIFY_MODEL = 'claude-haiku-4-5'  # 빠른 분류용 Haiku

_UA = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
)


def _normalize(kw: str) -> str:
    return re.sub(r'\s+', ' ', (kw or '').strip().lower())


# ──────────────────────────────────────────────────────────
# 1. Google Trends (pytrends) 한국 일간 급상승
# ──────────────────────────────────────────────────────────

def fetch_google_trends(limit: int = 30) -> list[dict]:
    try:
        from pytrends.request import TrendReq
    except Exception as e:
        log.warning(f'pytrends 임포트 실패: {e}')
        return []

    try:
        pt = TrendReq(hl='ko-KR', tz=540, retries=0)
        df = pt.trending_searches(pn='south_korea')
        if df is None or df.empty:
            return []
        kws = df[0].tolist()
    except Exception as e:
        log.warning(f'Google Trends 실패 (차단 가능): {e}')
        return []

    out = []
    seen: set[str] = set()
    for kw in kws:
        kw = (kw or '').strip()
        n = _normalize(kw)
        if not n or n in seen:
            continue
        seen.add(n)
        out.append({'keyword': kw, 'source': 'google_trends', 'related': []})
        if len(out) >= limit:
            break
    log.info(f'Google Trends: {len(out)}개')
    return out


# ──────────────────────────────────────────────────────────
# 2. Google Autocomplete (연관 키워드 확장)
# ──────────────────────────────────────────────────────────

def fetch_autocomplete(seed: str, limit: int = 8) -> list[str]:
    """Google 자동완성으로 seed 키워드의 연관어 확장."""
    url = (
        f'https://www.google.com/complete/search'
        f'?q={quote(seed)}&client=chrome&hl=ko&gl=kr'
    )
    try:
        r = requests.get(url, headers={'User-Agent': _UA}, timeout=6)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        log.debug(f'autocomplete "{seed}" 실패: {e}')
        return []

    # 응답: [query, [suggestions...], ..., metadata]
    suggestions = []
    if isinstance(data, list) and len(data) >= 2 and isinstance(data[1], list):
        for s in data[1]:
            s = (s or '').strip()
            if s and s.lower() != seed.lower():
                suggestions.append(s)
            if len(suggestions) >= limit:
                break
    return suggestions


# ──────────────────────────────────────────────────────────
# 3. pytrends related_queries (상승 쿼리)
# ──────────────────────────────────────────────────────────

def fetch_related_rising(seed: str, limit: int = 5) -> list[str]:
    try:
        from pytrends.request import TrendReq
    except Exception:
        return []
    try:
        pt = TrendReq(hl='ko-KR', tz=540, retries=0)
        pt.build_payload([seed], timeframe='now 7-d', geo='KR')
        rq = pt.related_queries()
        if not rq or seed not in rq:
            return []
        rising = rq[seed].get('rising')
        if rising is None or rising.empty:
            return []
        return rising['query'].head(limit).tolist()
    except Exception as e:
        log.debug(f'related_rising "{seed}" 실패: {e}')
        return []


# ──────────────────────────────────────────────────────────
# 4. YouTube Data API v3 인기 급상승 (한국 전체)
# ──────────────────────────────────────────────────────────

def fetch_youtube_trending(limit: int = 20) -> list[dict]:
    api_key = os.getenv('YOUTUBE_API_KEY', '').strip()
    if not api_key:
        return []
    try:
        from googleapiclient.discovery import build
        yt = build('youtube', 'v3', developerKey=api_key, cache_discovery=False)
        resp = yt.videos().list(
            part='snippet',
            chart='mostPopular',
            regionCode='KR',
            maxResults=50,
        ).execute()
    except Exception as e:
        log.warning(f'YouTube API 실패: {e}')
        return []

    out = []
    seen: set[str] = set()
    for item in resp.get('items', []):
        sn = item.get('snippet', {})
        title = (sn.get('title') or '').strip()
        if not title:
            continue
        # 40자 이내 핵심 구만
        kw = title[:40].rstrip(' |-·')
        n = _normalize(kw)
        if not n or n in seen:
            continue
        seen.add(n)
        out.append({'keyword': kw, 'source': 'youtube', 'related': []})
        if len(out) >= limit:
            break
    log.info(f'YouTube Trending: {len(out)}개')
    return out


# ──────────────────────────────────────────────────────────
# 5. Claude 카테고리 분류 (애드센스 안전 필터)
# ──────────────────────────────────────────────────────────

_CATEGORY_PROMPT = """다음은 한국어 트렌드 키워드 목록입니다. 각 키워드를 카테고리로 분류하세요.

허용 카테고리 (ALLOW):
  - "it" (IT·가전·디지털·스마트폰·AI)
  - "shopping" (쇼핑·생활용품·세일)
  - "travel" (여행·관광·호텔·항공)
  - "movie" (영화·드라마·OTT 작품 정보)
  - "game" (게임 출시·업데이트·공략)
  - "newproduct" (신제품 출시·리뷰)
  - "food" (요리·맛집·레시피)
  - "auto" (자동차·전기차)
  - "health" (건강·운동·다이어트 정보)
  - "finance" (재테크·부동산·세금·정책)
  - "guide" (팁·가이드·하우투)

차단 (BLOCK):
  - "celebrity" (연예인 가십·사생활·열애·이혼)
  - "politics" (정치·정당·선거·정치인)
  - "sports" (스포츠 경기결과·선수 이슈)
  - "crime" (사건사고·범죄·사망·사고)
  - "adult" (성인·도박·음란)
  - "controversy" (논란·분쟁·갈등)
  - "religion" (종교)
  - "other" (위 카테고리 어디에도 해당 없음·모호함)

키워드 목록:
{keywords}

출력 형식: JSON 배열만 출력. 다른 설명·코드블록·주석 금지.
[
  {{"keyword": "키워드1", "category": "it"}},
  {{"keyword": "키워드2", "category": "celebrity"}}
]
"""


def classify_keywords_for_tistory(keywords: list[str]) -> list[dict]:
    """Claude CLI 로 키워드를 카테고리 분류. 허용 카테고리만 반환."""
    if not keywords:
        return []

    allow = {'it', 'shopping', 'travel', 'movie', 'game',
             'newproduct', 'food', 'auto', 'health', 'finance', 'guide'}

    numbered = '\n'.join(f'{i+1}. {k}' for i, k in enumerate(keywords))
    prompt = _CATEGORY_PROMPT.format(keywords=numbered)

    try:
        result = subprocess.run(
            [CLAUDE_BIN, '--model', CLAUDE_CLASSIFY_MODEL, '-p', prompt],
            capture_output=True, text=True, timeout=60,
        )
        raw = (result.stdout or '').strip()
        m = re.search(r'\[[\s\S]*\]', raw)
        if not m:
            log.warning(f'[classify] JSON 배열 찾기 실패: {raw[:200]}')
            return []
        items = json.loads(m.group(0))
    except Exception as e:
        log.warning(f'[classify] 실패: {e}')
        return []

    kept = []
    for it in items:
        if not isinstance(it, dict):
            continue
        kw = str(it.get('keyword', '')).strip()
        cat = str(it.get('category', '')).strip().lower()
        if not kw or cat not in allow:
            continue
        kept.append({'keyword': kw, 'category': cat})
    log.info(f'[classify] 입력 {len(keywords)} → 허용 {len(kept)}개')
    return kept


# ──────────────────────────────────────────────────────────
# 통합: 핫 키워드 + 연관 키워드
# ──────────────────────────────────────────────────────────

def collect_hot_keywords(target_count: int = 6) -> list[dict]:
    """
    최종 반환: target_count 개의 검증된 핫 키워드.
    각 항목: {keyword, category, source, related[]}
    """
    pool: list[dict] = []
    seen: set[str] = set()

    def _add(item: dict):
        kw = item['keyword']
        # 너무 짧은 키워드 (3글자 이하) 는 본문/SEO 부적합
        if len(kw.strip()) < 4:
            return
        n = _normalize(kw)
        if not n or n in seen:
            return
        seen.add(n)
        pool.append(item)

    for item in fetch_google_trends(limit=30):
        _add(item)

    for item in fetch_youtube_trending(limit=20):
        _add(item)

    if not pool:
        log.warning('[hot] 풀 비어있음 — 모든 소스 실패')
        return []

    # Claude 카테고리 분류 → 허용만 필터
    classified = classify_keywords_for_tistory([p['keyword'] for p in pool])
    kw_to_cat = {c['keyword']: c['category'] for c in classified}

    allowed = []
    for p in pool:
        if p['keyword'] in kw_to_cat:
            p['category'] = kw_to_cat[p['keyword']]
            allowed.append(p)

    log.info(f'[hot] 풀 {len(pool)} → 허용 {len(allowed)}개, 목표 {target_count}')

    # 목표 개수만큼 추출 + 연관 키워드 붙이기
    picked = allowed[:target_count]
    for p in picked:
        seed = p['keyword']
        ac = fetch_autocomplete(seed, limit=6)
        rq = fetch_related_rising(seed, limit=4)
        rel = []
        seen_rel = set()
        for x in ac + rq:
            n = _normalize(x)
            if not n or n in seen_rel or n == _normalize(seed):
                continue
            seen_rel.add(n)
            rel.append(x)
            if len(rel) >= 8:
                break
        p['related'] = rel

    return picked


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

    picks = collect_hot_keywords(target_count=6)
    print(f'\n총 {len(picks)}개 확정:\n')
    for p in picks:
        print(f'  [{p["source"]:<13}] {p["category"]:<10} {p["keyword"]}')
        if p['related']:
            print(f'    연관: {", ".join(p["related"])}')
