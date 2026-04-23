"""
외부 트렌드 키워드 수집 — Google Trends (pytrends) + YouTube Data API v3.

핵심 규칙:
  • victor-jk DB 뉴스보다 외부 키워드가 우선.
  • 각 소스 실패는 빈 리스트 반환(예외 전파 금지) — trend_generator 가 폴백 결정.
  • 전자기기/IT 와 무관한 키워드(정치·스포츠·연예)는 필터링.

반환 포맷:
  [
    {"keyword": "갤럭시 Z폴드7", "source": "google_trends", "context": "..."},
    {"keyword": "아이폰 17 프로", "source": "youtube",      "context": "..."},
  ]
"""
from __future__ import annotations

import os
import logging
import re
from typing import Iterable

log = logging.getLogger(__name__)

# 전자기기/IT 관련 한글+영문 키워드 (부분일치)
_TECH_HINTS = (
    # 한글
    '스마트폰', '폰', '아이폰', '갤럭시', '픽셀', '샤오미', '원플러스',
    '노트북', '맥북', '그램', '울트라', '태블릿', '아이패드', '갤럭시탭',
    '이어폰', '헤드폰', '에어팟', '버즈', '스마트워치', '워치', '애플워치',
    'tv', 'oled', 'qled', 'lcd', '모니터', '디스플레이', '주사율',
    '카메라', '렌즈', '미러리스', '가전', '냉장고', '세탁기', '건조기',
    '에어컨', '공기청정기', '로봇청소기', '청소기', '전자레인지',
    '헤어드라이어', '면도기', '음식물처리기',
    '반도체', '칩', '프로세서', '배터리', '충전', '무선충전', '고속충전',
    '5g', '6g', 'wifi', '블루투스', 'ai', '인공지능', '챗봇',
    '폴더블', '접는', '플립', '폴드', '스펙', '리뷰', '출시',
    # 영문
    'iphone', 'galaxy', 'pixel', 'xiaomi', 'oneplus', 'oppo', 'vivo',
    'macbook', 'ipad', 'airpods', 'watch', 'gram', 'thinkpad',
    'foldable', 'flip', 'fold', 'ultra', 'pro', 'plus',
    'samsung', 'apple', 'google', 'sony', 'lg', 'dyson',
    'quest', 'vision', 'steamdeck', 'switch', 'playstation', 'xbox',
    'rtx', 'intel', 'amd', 'snapdragon', 'mediatek', 'exynos',
    'oled', 'qled', 'hdr', '4k', '8k',
)


def _is_tech_related(text: str) -> bool:
    if not text:
        return False
    low = text.lower()
    return any(h in low for h in _TECH_HINTS)


def _normalize(kw: str) -> str:
    """중복 판정용 정규화: 소문자 + 공백 정리."""
    return re.sub(r'\s+', ' ', kw.strip().lower())


# ──────────────────────────────────────────────────────────
# Google Trends (pytrends)
# ──────────────────────────────────────────────────────────

def fetch_google_trends(limit: int = 20) -> list[dict]:
    """
    Google Trends 한국 일간 급상승 검색어.
    pytrends 는 내부적으로 비공개 엔드포인트를 사용 — 429 차단 빈발.
    실패 시 빈 리스트 반환.
    """
    try:
        from pytrends.request import TrendReq
    except Exception as e:
        log.warning(f'pytrends 임포트 실패: {e}')
        return []

    try:
        # retries=0 — pytrends 4.9 + urllib3 2.x 는 method_whitelist kwarg 충돌
        pytrends = TrendReq(hl='ko-KR', tz=540, retries=0)
        # trending_searches: 국가별 일간 급상승
        df = pytrends.trending_searches(pn='south_korea')
        if df is None or df.empty:
            return []
        keywords = df[0].tolist()
    except Exception as e:
        log.warning(f'Google Trends 실패 (차단 가능): {e}')
        return []

    results = []
    for kw in keywords:
        kw = (kw or '').strip()
        if not kw:
            continue
        if not _is_tech_related(kw):
            continue
        results.append({
            'keyword': kw,
            'source':  'google_trends',
            'context': '구글 트렌드 한국 일간 급상승',
        })
        if len(results) >= limit:
            break
    log.info(f'Google Trends: {len(results)}개 (IT 필터 후)')
    return results


# ──────────────────────────────────────────────────────────
# YouTube Data API v3
# ──────────────────────────────────────────────────────────

def fetch_youtube_trending(limit: int = 20) -> list[dict]:
    """
    YouTube 한국 trending videos (Science & Technology 카테고리 우선).
    카테고리 ID 28 = Science & Technology.
    무료 quota 10K/일, 이 호출은 요청당 1 quota.
    """
    api_key = os.getenv('YOUTUBE_API_KEY', '').strip()
    if not api_key:
        log.warning('YOUTUBE_API_KEY 미설정')
        return []

    try:
        from googleapiclient.discovery import build
    except Exception as e:
        log.warning(f'googleapiclient 임포트 실패: {e}')
        return []

    results: list[dict] = []
    seen: set[str] = set()

    def _collect(category_id: str | None):
        try:
            yt = build('youtube', 'v3', developerKey=api_key, cache_discovery=False)
            kwargs = dict(
                part='snippet',
                chart='mostPopular',
                regionCode='KR',
                maxResults=50,
            )
            if category_id:
                kwargs['videoCategoryId'] = category_id
            resp = yt.videos().list(**kwargs).execute()
        except Exception as e:
            log.warning(f'YouTube 조회 실패 (cat={category_id}): {e}')
            return

        for item in resp.get('items', []):
            sn = item.get('snippet', {})
            title = (sn.get('title') or '').strip()
            if not title:
                continue
            # 태그는 원저자가 붙인 키워드 → 트렌드 힌트로 활용
            tags = sn.get('tags') or []
            blob = ' '.join([title] + tags)
            if not _is_tech_related(blob):
                continue
            # 제목에서 40자 이내 핵심 구 추출
            key = title[:40]
            norm = _normalize(key)
            if norm in seen:
                continue
            seen.add(norm)
            results.append({
                'keyword': key,
                'source':  'youtube',
                'context': f'유튜브 한국 인기 급상승 — {sn.get("channelTitle", "")}',
            })
            if len(results) >= limit:
                return

    _collect('28')   # Science & Technology
    if len(results) < limit:
        _collect(None)  # 전체 인기에서 tech 필터

    log.info(f'YouTube trending: {len(results)}개 (IT 필터 후)')
    return results[:limit]


# ──────────────────────────────────────────────────────────
# 통합
# ──────────────────────────────────────────────────────────

def collect_external_keywords(limit_per_source: int = 20) -> list[dict]:
    """두 소스 합쳐서 반환. 중복은 정규화 비교로 제거. 순서: Google Trends → YouTube."""
    out: list[dict] = []
    seen: set[str] = set()
    for src in (fetch_google_trends, fetch_youtube_trending):
        for item in src(limit_per_source):
            norm = _normalize(item['keyword'])
            if not norm or norm in seen:
                continue
            seen.add(norm)
            out.append(item)
    return out


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    items = collect_external_keywords()
    print(f'총 {len(items)}개')
    for i in items[:20]:
        print(f'  [{i["source"]:<14}] {i["keyword"]}')
