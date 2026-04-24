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

import html as _html
import json
import logging
import os
import re
import subprocess
from urllib.parse import quote

import requests

try:
    import feedparser  # Google News RSS · Naver DataLab 는 직접 파싱
except ImportError:
    feedparser = None

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
# 하드블록 패턴 (Claude 분류 호출 전 선필터 — 토큰·시간 절약)
# ──────────────────────────────────────────────────────────
_HARDBLOCK_PATTERNS = [
    # 정치·정부·정당
    r'국힘|국민의힘|민주당|정의당|개혁신당|조국혁신|윤석열|이재명|한동훈|'
    r'장동혁|배현진|주호영|오세훈|박지원|조희대|검찰|특검|수사|영장|기소|'
    r'재판|압수수색|국정감사|청문회|의원|당대표|대통령|대선|총선|지선|'
    r'지방선거|여야|야당|여당|탄핵|국회',
    # 사건사고·범죄·부정
    r'사망|숨져|숨진|살해|피살|시신|참사|폭행|성추행|성폭행|마약|탈세|사기|'
    r'구속|연행|체포|추락|실종|화재|폭발|붕괴|추돌|충돌사고|뺑소니|절도|'
    r'강도|학대|자살|극단선택',
    # 기업 부정적 노동·구조조정 이슈 (애드센스 민감)
    r'피바람|해고|감원|구조조정|파업|노조 집회|임금 체불|갑질|정리해고|'
    r'짐 싸라|희망퇴직',
    # 연예인 가십 주요 패턴
    r'열애|이혼|결혼설|임신설|사생활|결별|스캔들|소속사|매니저|'
    r'폭로|고소|법정|소송',
    # 스포츠 경기결과·선수 이슈
    r'홈런|타율|선발투수|프로야구|KBO|KBL|V리그|K리그|프로축구|우승|패배|득점왕|MVP',
    # 종교
    r'성경|목사|기독교|불교|천주교|힌두교|이슬람교',
]
_HARDBLOCK_RE = re.compile('|'.join(_HARDBLOCK_PATTERNS))


def _is_blocked(kw: str) -> bool:
    """하드블록 — 애드센스 정책상 확실히 부적합한 키워드."""
    return bool(_HARDBLOCK_RE.search(kw or ''))


# ──────────────────────────────────────────────────────────
# 1. Google Trends (pytrends) 한국 일간 급상승
# ──────────────────────────────────────────────────────────
#
# 2025~ Google 이 내부 엔드포인트 변경으로 pytrends.trending_searches 가
# 404 를 상시 반환. 환경변수 `PYTRENDS_ENABLED=1` 일 때만 시도하고, 기본은
# skip. related_queries 도 같은 엔드포인트 계열이라 상황 동일.

def fetch_google_trends(limit: int = 30) -> list[dict]:
    if os.getenv('PYTRENDS_ENABLED', '0') != '1':
        return []
    try:
        from pytrends.request import TrendReq
    except Exception as e:
        log.debug(f'pytrends 임포트 실패: {e}')
        return []

    try:
        pt = TrendReq(hl='ko-KR', tz=540, retries=0, timeout=(5, 8))
        df = pt.trending_searches(pn='south_korea')
        if df is None or df.empty:
            return []
        kws = df[0].tolist()
    except Exception as e:
        log.debug(f'Google Trends skip: {e}')
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
# 1-b. Google News RSS 한국 (주 소스)
# ──────────────────────────────────────────────────────────
#
# 공식 피드, API 키 불필요. 전체 헤드라인 + 토픽별(TECHNOLOGY/BUSINESS/
# ENTERTAINMENT/SPORTS/HEALTH/SCIENCE).  전체 제목에서 핵심 명사구만 추출
# 하여 seed 로 사용. Claude 분류기가 연예·정치·스포츠·사건사고 제외.

_GN_FEEDS = [
    ('top',           'https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko'),
    ('technology',    'https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ko&gl=KR&ceid=KR:ko'),
    ('business',      'https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko'),
    ('entertainment', 'https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=ko&gl=KR&ceid=KR:ko'),
    ('health',        'https://news.google.com/rss/headlines/section/topic/HEALTH?hl=ko&gl=KR&ceid=KR:ko'),
    ('science',       'https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=ko&gl=KR&ceid=KR:ko'),
]


def _strip_source(title: str) -> str:
    """Google News 제목 말미의 ' - 언론사' 제거."""
    # " - XXX뉴스" / " - 매일경제" 같은 패턴
    return re.sub(r'\s+-\s+[^-]+$', '', title).strip()


def fetch_google_news_rss(per_feed: int = 8) -> list[dict]:
    if feedparser is None:
        log.warning('feedparser 미설치 — Google News RSS skip')
        return []
    out: list[dict] = []
    seen: set[str] = set()
    for label, url in _GN_FEEDS:
        try:
            feed = feedparser.parse(url, request_headers={'User-Agent': _UA})
        except Exception as e:
            log.debug(f'Google News feed {label} 실패: {e}')
            continue
        count = 0
        for entry in feed.entries[:20]:
            title = _html.unescape(getattr(entry, 'title', '') or '').strip()
            if not title:
                continue
            kw = _strip_source(title)
            if len(kw) < 4 or len(kw) > 80:
                continue
            n = _normalize(kw)
            if n in seen:
                continue
            seen.add(n)
            out.append({
                'keyword': kw,
                'source':  f'gnews_{label}',
                'related': [],
            })
            count += 1
            if count >= per_feed:
                break
    log.info(f'Google News RSS: {len(out)}개 ({len(_GN_FEEDS)}개 피드)')
    return out


# ──────────────────────────────────────────────────────────
# 1-c. 네이버 뉴스 검색 API (Client ID/Secret 필요)
# ──────────────────────────────────────────────────────────
#
# DataLab 은 탐색(discovery)에 부적합 — 지정 키워드의 추이만 제공.
# 대신 '네이버 뉴스 검색 API' 로 범용 시드 쿼리별 최신 뉴스 제목을 수집.
# 결과 title 이 HTML(<b>태그 등) 포함이라 정리 후 사용.
#
# developers.naver.com 앱 등록 — 검색 API(search.news) 권한 필요.

_NAVER_CLIENT_ID     = os.getenv('NAVER_CLIENT_ID', '').strip()
_NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET', '').strip()

# 범용·안전 시드 쿼리 (쿼리당 네이버 뉴스 10건 → 7쿼리 ≈ 70건 풀)
_NAVER_NEWS_QUERIES = [
    '신제품',      # 전자기기·생활가전 출시
    '가전 할인',   # 쇼핑·세일
    '여행 추천',   # 여행
    '레시피',      # 요리·맛집
    '주식 전망',   # 재테크
    '자동차 신차', # 자동차
    '건강',        # 건강·운동
]

_HTML_TAG_RE = re.compile(r'<[^>]+>')


def _clean_naver_title(raw: str) -> str:
    t = _html.unescape(_HTML_TAG_RE.sub('', raw or ''))
    return re.sub(r'\s+', ' ', t).strip()


def fetch_naver_news_search(per_query: int = 10) -> list[dict]:
    """네이버 뉴스 검색 API 로 시드 쿼리별 최신 뉴스 제목 수집."""
    if not (_NAVER_CLIENT_ID and _NAVER_CLIENT_SECRET):
        log.debug('NAVER_CLIENT_ID/SECRET 미설정 — Naver News skip')
        return []

    out: list[dict] = []
    seen: set[str] = set()
    for q in _NAVER_NEWS_QUERIES:
        try:
            r = requests.get(
                'https://openapi.naver.com/v1/search/news.json',
                headers={
                    'X-Naver-Client-Id':     _NAVER_CLIENT_ID,
                    'X-Naver-Client-Secret': _NAVER_CLIENT_SECRET,
                },
                params={'query': q, 'display': per_query, 'sort': 'date'},
                timeout=8,
            )
            if r.status_code != 200:
                log.debug(f'[naver-news] {q} {r.status_code}: {r.text[:120]}')
                continue
            items = r.json().get('items', [])
        except Exception as e:
            log.debug(f'[naver-news] {q} 오류: {e}')
            continue

        for it in items:
            title = _clean_naver_title(it.get('title', ''))
            if len(title) < 4 or len(title) > 80:
                continue
            n = _normalize(title)
            if n in seen:
                continue
            seen.add(n)
            out.append({
                'keyword': title,
                'source':  f'naver_news_{q}',
                'related': [],
            })
    if out:
        log.info(f'Naver News Search: {len(out)}개 ({len(_NAVER_NEWS_QUERIES)}쿼리)')
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


_CLASSIFY_BATCH = 25  # Haiku 가 60초 안에 JSON 출력 가능한 안전치


def _classify_batch(keywords: list[str]) -> list[dict]:
    allow = {'it', 'shopping', 'travel', 'movie', 'game',
             'newproduct', 'food', 'auto', 'health', 'finance', 'guide'}
    numbered = '\n'.join(f'{i+1}. {k}' for i, k in enumerate(keywords))
    prompt = _CATEGORY_PROMPT.format(keywords=numbered)
    try:
        result = subprocess.run(
            [CLAUDE_BIN, '--model', CLAUDE_CLASSIFY_MODEL, '-p', prompt],
            capture_output=True, text=True, timeout=90,
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
    return kept


def classify_keywords_for_tistory(keywords: list[str]) -> list[dict]:
    """Claude CLI 로 키워드를 카테고리 분류. 허용 카테고리만 반환.

    대용량 입력은 _CLASSIFY_BATCH 크기로 배치 분할 (Haiku timeout 방지).
    """
    if not keywords:
        return []
    kept: list[dict] = []
    for i in range(0, len(keywords), _CLASSIFY_BATCH):
        batch = keywords[i:i + _CLASSIFY_BATCH]
        kept.extend(_classify_batch(batch))
    log.info(f'[classify] 입력 {len(keywords)} → 허용 {len(kept)}개 '
             f'({(len(keywords)+_CLASSIFY_BATCH-1)//_CLASSIFY_BATCH}배치)')
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
    blocked_ct = 0

    def _add(item: dict):
        nonlocal blocked_ct
        kw = item['keyword']
        # 너무 짧은 키워드 (3글자 이하) 는 본문/SEO 부적합
        if len(kw.strip()) < 4:
            return
        # 하드블록 (정치·사건사고·연예가십·스포츠·종교)
        if _is_blocked(kw):
            blocked_ct += 1
            return
        n = _normalize(kw)
        if not n or n in seen:
            return
        seen.add(n)
        pool.append(item)

    # 우선순위: Google News RSS → YouTube Trending → Naver News → pytrends(비활성)
    for item in fetch_google_news_rss(per_feed=5):
        _add(item)

    for item in fetch_youtube_trending(limit=15):
        _add(item)

    for item in fetch_naver_news_search(per_query=5):
        _add(item)

    for item in fetch_google_trends(limit=30):
        _add(item)

    log.info(f'[hot] 풀 {len(pool)}개 (하드블록 제거 {blocked_ct}건)')

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
