"""WordPress REST API 발행 모듈."""
import os
import re
import base64
import logging
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

WP_URL       = os.getenv('WP_URL', 'https://blog.victor-jk.com')
WP_USER      = os.getenv('WP_USER', 'Victor-JK')
WP_PASS      = os.getenv('WP_APP_PASSWORD', '')
PIXABAY_KEY  = os.getenv('PIXABAY_API_KEY', '55513176-cde8c9791e54c45fdb2a0cd46')

log = logging.getLogger(__name__)

_token = base64.b64encode(f'{WP_USER}:{WP_PASS}'.encode()).decode()
HEADERS = {
    'Authorization': f'Basic {_token}',
    'Content-Type': 'application/json',
}

_UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

INDEXNOW_KEY = os.getenv('INDEXNOW_KEY', '').strip()

import random as _random

try:
    from catalog_images import CATALOG_IMAGES as _CATALOG_IMAGES
except ImportError:
    _CATALOG_IMAGES = {}


def _api(path: str) -> str:
    return f'{WP_URL}/wp-json/wp/v2/{path}'


def _indexnow_ping(url: str) -> None:
    """IndexNow 핑 (Bing·네이버 등 호환 검색엔진에 색인 요청). 실패는 무시."""
    if not INDEXNOW_KEY or not url:
        return
    try:
        from urllib.parse import urlparse
        host = urlparse(url).hostname or ''
        if not host:
            return
        requests.get(
            'https://api.indexnow.org/indexnow',
            params={
                'url':         url,
                'key':         INDEXNOW_KEY,
                'keyLocation': f'https://{host}/{INDEXNOW_KEY}.txt',
            },
            timeout=8,
        )
    except Exception as e:
        log.warning(f'IndexNow 핑 실패: {e}')


# ──────────────────────────────────────────────────────────
# 웹 검색 이미지 (우선순위 1·2)
# ──────────────────────────────────────────────────────────

# 브랜드별 공식 사이트 도메인 (검색 타겟팅용)
_BRAND_SITES = {
    'Samsung':  'samsung.com',
    'Apple':    'apple.com',
    'LG':       'lg.com',
    'Sony':     'sony.com',
    'Google':   'store.google.com',
    'Xiaomi':   'xiaomi.com',
    'ASUS':     'asus.com',
    'Lenovo':   'lenovo.com',
    'Dell':     'dell.com',
    'HP':       'hp.com',
    'Microsoft':'microsoft.com',
    'OnePlus':  'oneplus.com',
    'Motorola': 'motorola.com',
    'Huawei':   'huawei.com',
    'Oppo':     'oppo.com',
    'Vivo':     'vivo.com',
    'Realme':   'realme.com',
    'Nothing':  'nothing.tech',
    'Garmin':   'garmin.com',
    'Bose':     'bose.com',
    'JBL':      'jbl.com',
    'Sennheiser':'sennheiser.com',
}

_CATEGORY_QUERIES = {
    'smartphone':     'smartphone technology',
    'laptop':         'laptop computer technology',
    'tablet':         'tablet computer technology',
    'earphone':       'earphones headphones music',
    'smartwatch':     'smartwatch wearable technology',
    'tv':             'television OLED QLED display',
    'monitor':        'computer monitor display screen',
    'camera':         'camera photography mirrorless',
    'gaming_console': 'gaming console video game',
    'speaker':        'speaker soundbar audio',
    'refrigerator':   'refrigerator kitchen appliance',
    'washing_machine':'washing machine laundry appliance',
    'air_conditioner':'air conditioner cooling appliance',
    'air_purifier':   'air purifier clean indoor',
    'robot_vacuum':   'robot vacuum cleaner smart home',
    'vacuum':         'vacuum cleaner cordless',
    'microwave':      'microwave oven countertop appliance',
    'hair_dryer':     'hair dryer styling beauty',
    'electric_shaver':'electric shaver grooming',
    'food_processor': 'food waste processor kitchen',
}

# Pixabay 결과 검증용: 각 카테고리에 대해 hit.tags 에 최소 1개는 들어있어야 통과
_CATEGORY_TAGS = {
    'smartphone':     ['smartphone', 'phone', 'mobile phone', 'mobile', 'cellphone'],
    'laptop':         ['laptop', 'notebook', 'computer'],
    'tablet':         ['tablet', 'ipad'],
    'earphone':       ['earphone', 'earphones', 'earbuds', 'headphone', 'headphones', 'headset'],
    'smartwatch':     ['smartwatch', 'watch', 'wristwatch'],
    'tv':             ['tv', 'television', 'hdtv', 'oled', 'qled', 'flat screen'],
    'monitor':        ['monitor', 'computer monitor', 'desktop'],
    'camera':         ['camera', 'photography', 'dslr', 'mirrorless', 'lens'],
    'gaming_console': ['console', 'gaming', 'game console', 'controller', 'playstation', 'xbox', 'nintendo'],
    'speaker':        ['speaker', 'loudspeaker', 'audio', 'sound', 'soundbar'],
    'refrigerator':   ['refrigerator', 'fridge', 'kitchen'],
    'washing_machine':['washing machine', 'washer', 'laundry', 'washing'],
    'air_conditioner':['air conditioner', 'aircon', 'conditioner', 'hvac', 'cooling'],
    'air_purifier':   ['air purifier', 'purifier', 'hepa', 'filter'],
    'robot_vacuum':   ['robot', 'vacuum', 'vacuum cleaner', 'cleaner'],
    'vacuum':         ['vacuum', 'vacuum cleaner', 'cleaner'],
    'microwave':      ['microwave', 'oven'],
    'hair_dryer':     ['hair dryer', 'hairdryer', 'dryer', 'hair'],
    'electric_shaver':['shaver', 'razor', 'grooming'],
    'food_processor': ['food processor', 'processor', 'kitchen', 'blender', 'mixer'],
}


def _pixabay_tag_match(hit: dict, required_tags: list[str]) -> bool:
    """Pixabay hit 의 tags(콤마 구분)에 required 중 하나라도 포함되면 통과."""
    if not required_tags:
        return True
    tag_str = (hit.get('tags') or '').lower()
    return any(t in tag_str for t in required_tags)


def _extract_og_image(url: str) -> str:
    """웹 페이지에서 og:image 메타 태그 URL 추출."""
    try:
        r = requests.get(url, headers={'User-Agent': _UA}, timeout=10, allow_redirects=True)
        # property="og:image" content="..."  또는 반대 순서
        m = re.search(
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](https?://[^"\'>\s]+)',
            r.text,
        )
        if not m:
            m = re.search(
                r'<meta[^>]+content=["\'](https?://[^"\'>\s]+)[^>]+property=["\']og:image["\']',
                r.text,
            )
        if m:
            return m.group(1)
    except Exception:
        pass
    return ''


def _ddg_search_urls(query: str, limit: int = 3) -> list[str]:
    """DuckDuckGo HTML 검색 결과에서 외부 URL 목록 반환."""
    try:
        r = requests.get(
            'https://html.duckduckgo.com/html/',
            params={'q': query},
            headers={'User-Agent': _UA},
            timeout=12,
        )
        # DDG HTML 결과 링크: <a class="result__a" href="https://...">
        urls = re.findall(r'<a[^>]+class="result__a"[^>]+href="(https?://[^"]+)"', r.text)
        if not urls:
            # 일부 버전에서는 href에 직접 URL
            urls = re.findall(r'href="(https?://(?!duckduckgo\.com)[^"]{10,})"', r.text)
        return urls[:limit]
    except Exception:
        return []


def _is_usable_image(url: str) -> bool:
    """SVG·GIF 제외, 실제 래스터 이미지만 허용."""
    low = url.lower().split('?')[0]
    return bool(url) and not low.endswith('.svg') and not low.endswith('.gif')


def _product_tokens(brand: str, model: str) -> list[str]:
    """브랜드+모델에서 검증용 핵심 토큰(2자 이상, 불용어 제외) 추출."""
    stop = {'the', 'pro', 'max', 'plus', 'mini', 'lite', 'ultra', 'edge',
            'new', 'inch', 'gen', 'and', 'with', 'for', '5g'}
    text = f'{brand} {model}'.lower()
    tokens = re.findall(r'[a-z0-9]+', text)
    return [t for t in tokens if len(t) >= 2 and t not in stop]


def _image_matches(url: str, brand: str, model: str, context: str = '') -> bool:
    """이미지 URL 이 제품과 매칭되는지 검증 (URL 만).

    - 핵심 토큰(브랜드+모델 분해)의 과반이 **URL 에 직접 포함**되어야 통과.
    - context 파라미터는 호환성 유지용으로만 받고 검증에는 사용하지 않음.
      (이전에는 context 에 검색 query 를 넣어 우회가 발생: Pro Max 제품에 Pro 이미지 등)
    """
    del context  # 의도적 미사용 — 과거 버그 방지
    tokens = _product_tokens(brand, model)
    if not tokens:
        return False
    hay  = url.lower()
    hits = sum(1 for t in tokens if t in hay)
    return hits >= max(2, (len(tokens) + 1) // 2)


def _wikipedia_image(query: str, brand: str = '') -> str:
    """Wikipedia 검색 API로 제품 이미지 URL 반환. SVG 제외."""
    try:
        sr = requests.get(
            'https://en.wikipedia.org/w/api.php',
            params={
                'action':   'query',
                'list':     'search',
                'srsearch': query,
                'srlimit':  '3',
                'format':   'json',
            },
            headers={'User-Agent': _UA},
            timeout=8,
        )
        results = sr.json().get('query', {}).get('search', [])
        if not results:
            return ''

        query_words = set(query.lower().split())
        if brand:
            query_words.add(brand.lower())

        title = ''
        for result in results:
            t = result['title']
            if query_words & set(t.lower().split()):
                title = t
                break
        if not title:
            return ''

        ir = requests.get(
            'https://en.wikipedia.org/api/rest_v1/page/summary/' + title.replace(' ', '_'),
            headers={'User-Agent': _UA},
            timeout=8,
        )
        summary = ir.json()
        # originalimage 우선, thumbnail 폴백 — SVG 제외
        for key in ('originalimage', 'thumbnail'):
            thumb = summary.get(key, {}).get('source', '')
            if thumb and _is_usable_image(thumb):
                log.info(f'Wikipedia 이미지: {title} → {thumb[:80]}')
                return thumb
        return ''
    except Exception as e:
        log.warning(f'Wikipedia 검색 실패: {e}')
        return ''


def fetch_web_image_url(model: str, brand: str) -> str:
    """
    우선순위:
    1. DuckDuckGo 인스턴트 앤서 API (인식된 제품만 해당)
    2. Wikipedia 검색 API → 제품 썸네일
    3. DuckDuckGo 웹 검색 → og:image 스크래핑 (브랜드 공식 사이트 우선)
    """
    site = _BRAND_SITES.get(brand, '')

    # 모델명에 브랜드가 이미 포함된 경우 중복 방지
    ddg_query = model if model.lower().startswith(brand.lower()) else f'{brand} {model}'

    # ── 1. DDG 인스턴트 앤서 ──
    try:
        r = requests.get(
            'https://api.duckduckgo.com/',
            params={'q': ddg_query, 'format': 'json', 'no_html': '1', 'skip_disambig': '1'},
            timeout=8,
        )
        data = r.json()
        img = data.get('Image', '')
        if img:
            if img.startswith('/'):
                img = 'https://duckduckgo.com' + img
            if img.startswith('http'):
                log.info(f'DDG 인스턴트 이미지: {img[:80]}')
                return img
    except Exception as e:
        log.warning(f'DDG API 실패: {e}')

    # ── 2. Wikipedia 검색 ──
    img = _wikipedia_image(ddg_query, brand)
    if img:
        return img

    # ── 3. DDG 웹 검색 → og:image ──
    queries = []
    if site:
        queries.append(f'{ddg_query} site:{site}')
    queries.append(f'{ddg_query} official specifications')
    queries.append(f'{ddg_query} review')
    queries.append(f'{ddg_query} press image')
    queries.append(f'{ddg_query} product photo')

    for query in queries:
        for url in _ddg_search_urls(query, limit=3):
            img = _extract_og_image(url)
            if img and _is_usable_image(img):
                log.info(f'웹 OG 이미지: {img[:80]} (from {url[:60]})')
                return img

    return ''


# ──────────────────────────────────────────────────────────
# Unsplash 이미지 검색 (Pixabay 다음 최후 폴백)
# ──────────────────────────────────────────────────────────

_UNSPLASH_QUERIES = {
    'smartphone':     'smartphone',
    'laptop':         'laptop computer',
    'tablet':         'tablet technology',
    'earphone':       'headphones earphones',
    'smartwatch':     'smartwatch',
    'tv':             'television screen',
    'monitor':        'computer monitor',
    'camera':         'camera photography',
    'gaming_console': 'gaming controller',
    'speaker':        'speaker audio',
    'refrigerator':   'refrigerator kitchen',
    'washing_machine':'laundry washing machine',
    'air_conditioner':'air conditioner',
    'air_purifier':   'air purifier clean',
    'robot_vacuum':   'robot vacuum',
    'vacuum':         'vacuum cleaner',
    'microwave':      'microwave oven',
    'hair_dryer':     'hair dryer',
    'electric_shaver':'electric shaver',
    'food_processor': 'kitchen appliance',
}


def _fetch_unsplash_image(category: str) -> str:
    """Unsplash Source API (무료, 키 불필요) — 카테고리별 고화질 사진."""
    query = _UNSPLASH_QUERIES.get(category, 'technology gadget')
    try:
        r = requests.get(
            f'https://source.unsplash.com/800x600/?{query.replace(" ", ",")}',
            headers={'User-Agent': _UA},
            timeout=12,
            allow_redirects=True,
        )
        url = r.url
        if url and _is_usable_image(url) and r.status_code == 200:
            log.info(f'Unsplash 이미지: {url[:80]}')
            return url
    except Exception as e:
        log.warning(f'Unsplash 실패: {e}')
    return ''


# ──────────────────────────────────────────────────────────
# Pixabay 이미지 검색 (폴백)
# ──────────────────────────────────────────────────────────

def fetch_pixabay_image_url(product: dict) -> str:
    """Pixabay 카테고리 폴백 (첫 결과만). _iter_pixabay_candidates 의 래퍼."""
    for url in _iter_pixabay_candidates(product.get('category', 'smartphone')):
        return url
    return ''


def _iter_pixabay_candidates(category: str):
    """Pixabay 카테고리 쿼리로 검색 후 **tags 에 카테고리 키워드 포함된 hit 만** yield.

    이전에는 _random.choice(hits) 로 첫 hit 를 그대로 썼으나, Pixabay 는
    쿼리와 무관한 연관 이미지(예: 'tv' 검색 시 거실 인테리어)를 자주 상위에
    올림. hit.tags 필드를 검증해 카테고리 키워드가 명시된 것만 후보로 남김.

    검증 실패 시 None/빈 반복자 → 호출측은 탈락(해당 주제 미발행).
    """
    query    = _CATEGORY_QUERIES.get(category, 'technology gadget')
    required = _CATEGORY_TAGS.get(category, [])

    try:
        r = requests.get(
            'https://pixabay.com/api/',
            params={
                'key':         PIXABAY_KEY,
                'q':           query,
                'image_type':  'photo',
                'orientation': 'horizontal',
                'per_page':    30,
                'safesearch':  'true',
            },
            timeout=10,
        )
        hits = r.json().get('hits', [])
    except Exception as e:
        log.warning(f'Pixabay 카테고리 검색 실패 ({query}): {e}')
        return

    matched = [h for h in hits if _pixabay_tag_match(h, required)]
    if not matched:
        log.warning(f'Pixabay 태그 검증 통과 0건 — 탈락 ({category}, query={query!r})')
        return

    log.info(f'Pixabay 태그 검증: {len(matched)}/{len(hits)} 통과 ({category})')
    picks = _random.sample(matched, min(5, len(matched)))
    for hit in picks:
        url = hit.get('webformatURL', '')
        if url:
            yield url


def _iter_image_urls_product(product: dict):
    """스펙 제품 이미지 후보 URL 을 우선순위 순으로 yield.

    단계:
      1. catalog_images 매핑 (slug별 공식 URL, 100% 정확)
      2. 웹검색 (Wikipedia/DDG/og) + 토큰 검증
      3. Pixabay 카테고리 폴백 — 태그 검증 통과한 후보만

    검증 실패가 누적되면 yield 없이 끝 → 호출측은 업로드 실패 처리.
    D1' 큐 필터에서는 이 이터레이터가 첫 URL 도 안 내면 "탈락" 으로 간주.
    Unsplash 폴백은 태그 검증 불가(해시 URL)로 제거. 품질 미달 주제는
    발행 안 함이 기본 정책.
    """
    model    = product.get('model', '')
    brand    = product.get('brand', '')
    category = product.get('category', 'smartphone')
    slug     = product.get('slug', '')

    fixed = (product.get('image_url') or _CATALOG_IMAGES.get(slug, '') or '').strip()
    if fixed and _is_usable_image(fixed):
        log.info(f'[1/3] catalog image_url: {brand} {model}')
        yield fixed

    img = fetch_web_image_url(model, brand)
    if img and _image_matches(img, brand, model):
        log.info(f'[2/3] 웹검색 검증 통과: {brand} {model}')
        yield img
    elif img:
        log.warning(f'웹 이미지 검증 실패, 다음 폴백: {brand} {model}')

    yielded_any = False
    for url in _iter_pixabay_candidates(category):
        yielded_any = True
        log.info(f'[3/3] Pixabay 검증 통과: {category}')
        yield url
    if not yielded_any:
        log.warning(f'[product] 모든 후보 탈락: {brand} {model}')


def _get_image_url(product: dict) -> str:
    """첫 후보 URL만 반환 (검증/재사용 용). 발행 경로는 _iter_image_urls_product 사용."""
    for url in _iter_image_urls_product(product):
        return url
    return ''


# ──────────────────────────────────────────────────────────
# WordPress 미디어 업로드
# ──────────────────────────────────────────────────────────

def upload_image_from_url(image_url: str, alt_text: str = '', filename_base: str = '') -> int:
    """이미지 URL을 WP 미디어 라이브러리에 업로드, media ID 반환.

    - alt_text: WP attachment 의 alt 필드(_wp_attachment_image_alt) 설정에 사용.
      한글 포함 가능. SEO/접근성 핵심.
    - filename_base: 파일명 베이스 (ASCII). 미지정 시 alt_text 에서 ASCII 추출.
    """
    try:
        img_r = requests.get(image_url, headers={'User-Agent': _UA}, timeout=15)
        img_r.raise_for_status()
        img_data = img_r.content

        ext = image_url.split('?')[0].rsplit('.', 1)[-1].lower()
        if ext not in ('jpg', 'jpeg', 'png', 'webp'):
            ext = 'jpg'
        mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                'png': 'image/png', 'webp': 'image/webp'}.get(ext, 'image/jpeg')

        base = filename_base or alt_text
        safe_name = re.sub(r'[^\x00-\x7F]', '', base)
        safe_name = re.sub(r'[^\w\-]', '_', safe_name)[:60] or 'image'
        headers = {
            'Authorization':       HEADERS['Authorization'],
            'Content-Type':        mime,
            'Content-Disposition': f'attachment; filename="{safe_name}.{ext}"',
        }
        r = requests.post(_api('media'), data=img_data, headers=headers, timeout=30)
        if r.status_code not in (200, 201):
            log.warning(f'이미지 업로드 실패: {r.status_code}')
            return 0
        media_id = r.json().get('id', 0)
        log.info(f'이미지 업로드 성공: media_id={media_id}')

        # alt 필드 설정 (SEO / 접근성)
        if media_id and alt_text:
            try:
                requests.post(
                    _api(f'media/{media_id}'),
                    json={'alt_text': alt_text, 'title': alt_text},
                    headers=HEADERS,
                    timeout=10,
                )
            except Exception as e:
                log.warning(f'alt 메타 설정 실패: {e}')
        return media_id
    except Exception as e:
        log.warning(f'이미지 업로드 오류: {e}')
    return 0


def _upload_first_ok(url_iter, alt_text: str = '', filename_base: str = '',
                     vision_topic: str = '') -> int:
    """후보 URL 순회하며 업로드 성공하는 첫 URL 의 media_id 반환.

    개별 URL 이 429/timeout/404 등으로 실패해도 다음 후보로 자동 폴백.
    모든 후보 소진 시 0 반환.

    vision_topic 이 주어지면 업로드 직전 Claude 비전으로 주제 적합도를 판정 —
    부적합 판정 시 다음 후보로 건너뜀. 판정 실패/타임아웃은 fail-open(통과).
    """
    tried = 0
    rejected = 0
    for url in url_iter:
        if not url:
            continue
        tried += 1
        if vision_topic:
            from content_generator import check_image_fits
            if not check_image_fits(url, vision_topic):
                rejected += 1
                continue
        media_id = upload_image_from_url(url, alt_text=alt_text, filename_base=filename_base)
        if media_id:
            if rejected:
                log.info(f'[upload] 비전 게이트로 {rejected}건 거부 후 채택')
            return media_id
        log.warning(f'[upload {tried}] 실패, 다음 후보 시도')
    if tried == 0:
        log.error('이미지 후보 없음')
    else:
        log.error(f'이미지 후보 {tried}개 모두 실패 (비전 거부 {rejected}건 포함)')
    return 0


# ──────────────────────────────────────────────────────────
# taxonomy 헬퍼
# ──────────────────────────────────────────────────────────

def get_or_create_term(name: str, taxonomy: str) -> int:
    """taxonomy 용어 ID를 반환, 없으면 생성."""
    r = requests.get(_api(taxonomy), params={'slug': name}, headers=HEADERS, timeout=10)
    items = r.json()
    if isinstance(items, list) and items:
        return items[0]['id']
    r = requests.post(_api(taxonomy), json={'name': name, 'slug': name}, headers=HEADERS, timeout=10)
    return r.json().get('id', 0)


# ──────────────────────────────────────────────────────────
# 발행
# ──────────────────────────────────────────────────────────

# 기술 주제 키워드 → Pixabay 이미지 쿼리 매핑
# 매칭 우선순위 = dict insertion order. 구체·복합어 먼저 → 포괄 키워드 나중.
_TECH_IMAGE_QUERIES = {
    # ── 가전 카테고리 (구체 우선, slug 영문도 포함) ──
    '공기청정기':       'air purifier hepa filter',
    'air-purifier':     'air purifier hepa filter',
    'air purifier':     'air purifier hepa filter',
    '로봇청소기':       'robot vacuum cleaner',
    'robot-vacuum':     'robot vacuum cleaner',
    'robot vacuum':     'robot vacuum cleaner',
    '식기세척기':       'dishwasher kitchen',
    'dishwasher':       'dishwasher kitchen',
    '전자레인지':       'microwave oven countertop appliance',
    'microwave':        'microwave oven countertop appliance',
    '음식물처리기':     'food waste processor kitchen',
    'food-waste':       'food waste processor kitchen',
    '에어컨':           'split air conditioner wall mounted',
    'air-conditioner':  'split air conditioner wall mounted',
    'air conditioner':  'split air conditioner wall mounted',
    '세탁기':           'washing machine laundry',
    'washing-machine':  'washing machine laundry',
    'washing machine':  'washing machine laundry',
    '건조기':           'clothes dryer laundry',
    'dryer':            'clothes dryer laundry',
    '냉장고':           'refrigerator kitchen',
    'refrigerator':     'refrigerator kitchen',
    '밥솥':             'rice cooker kitchen',
    'rice-cooker':      'rice cooker kitchen',
    '헤어드라이어':     'hair dryer beauty',
    'hair-dryer':       'hair dryer beauty',
    '면도기':           'electric shaver grooming',
    'shaver':           'electric shaver grooming',
    '청소기':           'vacuum cleaner home',
    'vacuum':           'vacuum cleaner home',
    '제습기':           'dehumidifier humidity home',
    'dehumidifier':     'dehumidifier humidity home',
    '정수기':           'water purifier kitchen',
    'water-purifier':   'water purifier kitchen',
    '비데':             'bidet toilet electronic',
    '안마의자':         'massage chair relax',
    '커피머신':         'coffee machine espresso',

    # ── 디스플레이·영상 ──
    '사운드바':         'soundbar audio home theater',
    'soundbar':         'soundbar audio home theater',
    'oled':             'OLED television display',
    'qled':             'QLED television display',
    'amoled':           'AMOLED display screen',
    '티비':             'television living room',
    'tv':               'television living room',
    '모니터':           'computer monitor desk',
    'monitor':          'computer monitor desk',
    '디스플레이':       'display screen technology',
    '주사율':           'gaming monitor display',
    'ltpo':             'smartwatch display',
    'hdr':              'HDR display television',

    # ── 모바일·웨어러블 ──
    '스마트워치':       'smartwatch wrist technology',
    'smartwatch':       'smartwatch wrist technology',
    '스마트밴드':       'fitness tracker wristband',
    '에어팟':           'wireless earbuds apple',
    'airpods':          'wireless earbuds apple',
    '갤럭시 버즈':      'wireless earbuds case',
    '버즈':             'wireless earbuds case',
    '이어폰':           'wireless earbuds headphone',
    'earphone':         'wireless earbuds headphone',
    'earbuds':          'wireless earbuds headphone',
    '헤드폰':           'headphones music audio',
    'headphone':        'headphones music audio',
    'headset':          'gaming headset audio',
    '헤드셋':           'gaming headset audio',
    '아이폰':           'smartphone apple modern',
    'iphone':           'smartphone apple modern',
    '갤럭시':           'smartphone samsung modern',
    'galaxy':           'smartphone samsung modern',
    '스마트폰':         'smartphone mobile device',
    'smartphone':       'smartphone mobile device',
    '아이패드':         'tablet apple reading',
    'ipad':             'tablet apple reading',
    '태블릿':           'tablet computer reading',
    'tablet':           'tablet computer reading',
    '맥북':             'macbook laptop apple',
    'macbook':          'macbook laptop apple',
    '노트북':           'laptop computer work',
    'laptop':           'laptop computer work',

    # ── 스피커·카메라·게임 ──
    '블루투스 스피커': 'bluetooth speaker audio',
    '스피커':           'bluetooth speaker audio',
    'speaker':          'bluetooth speaker audio',
    # 복합어 우선 (딕셔너리 순회 시 먼저 매칭)
    '카메라 센서':      'camera sensor image',
    '이미지 센서':      'camera sensor image',
    '풀프레임':         'camera sensor image',
    'aps-c':            'camera sensor image',
    '미러리스':         'mirrorless camera photography',
    '카메라':           'camera lens photography',
    'camera':           'camera lens photography',
    '센서':             'camera sensor image',
    '화소':             'camera photography',
    '손떨림':           'camera stabilization',
    '게임기':           'game console controller',
    '콘솔':             'game console controller',
    'playstation':      'playstation game console',
    'xbox':             'xbox game console',
    '닌텐도':           'nintendo switch console',

    # ── 위치 추적기 (apple → 사과 오검출 방지) ──
    '에어태그':         'bluetooth tracker keychain',
    'airtag':           'bluetooth tracker keychain',
    '스마트태그':       'bluetooth tracker keychain',
    'smarttag':         'bluetooth tracker keychain',
    'tile tracker':     'bluetooth tracker keychain',
    '분실 추적':        'bluetooth tracker keychain',
    'find my':          'bluetooth tracker keychain',
    '위치 추적':        'bluetooth tracker keychain',

    # ── 주변기기·연결 ──
    '키보드':           'mechanical keyboard desk',
    'keyboard':         'mechanical keyboard desk',
    '마우스':           'computer mouse desk',
    '프린터':           'office printer',
    'printer':          'office printer',
    '충전기':           'usb charger cable',
    '보조배터리':       'power bank portable',
    'power-bank':       'power bank portable',
    '배터리':           'battery charging technology',
    '충전':             'wireless charging',
    '5g':               '5G network mobile',
    '6g':               '6G network future',
    'wifi':             'wifi router network',
    '블루투스':         'bluetooth wireless',
    'bluetooth':        'bluetooth wireless',
    'usb':              'USB cable connector',

    # ── 반도체·컴퓨팅 ──
    '프로세서':         'computer processor chip',
    '반도체':           'semiconductor chip wafer',
    'semiconductor':    'semiconductor chip wafer',
    '칩':               'semiconductor chip',
    'cpu':              'computer processor',
    'gpu':              'graphics card GPU',
    'ram':              'computer memory RAM',
    'ssd':              'SSD storage technology',

    # ── 오디오·기타 기술 개념 ──
    '공간 음향':        'spatial audio headphones',
    '공간음향':         'spatial audio headphones',
    'spatial audio':    'spatial audio headphones',
    '돌비':             'home theater audio',
    'anc':              'headphones noise cancelling',
    '노이즈':           'audio sound wave',

    # ── 효율·친환경·안전 ──
    '냉각':             'cooling fan heat',
    '방열':             'cooling technology',
    '방수':             'waterproof electronics',
    '재활용':           'recycled electronics circuit',
    '친환경':           'eco friendly electronics technology',
    '에너지':           'energy efficiency home',
    '에너지 효율':     'energy efficiency home',
    '인버터':           'inverter technology efficient',
    '필터':             'air filter purifier',
    '흡입':             'vacuum cleaner suction',
    '로봇':             'robot home automation',
    '미세먼지':         'air pollution particulate',
    '냉매':             'refrigerator compressor',

    # ── 보증·서비스·에너지 ──
    '보증':             'warranty document contract',
    'as 센터':          'customer service repair desk',
    'a/s':              'customer service repair desk',
    '에너지 소비효율':  'energy efficiency rating label',
    '에너지':           'energy efficiency appliance',
    '등급':             'energy rating label',

    # ── 조명·스마트홈 ──
    '스마트 조명':      'smart light bulb connected',
    '필립스 휴':        'philips hue smart light',
    '시라이트':         'smart light bulb',
    '조명':             'lamp lighting home',

    # ── 보안·사기 (생활 정보) ──
    '보이스피싱':       'phone scam fraud security',
    '피싱':             'phishing cyber security',

    # ── 생활/식품 ──
    '생수':             'bottled water glass',
    '미네랄':           'bottled water mineral',
    '유산균':           'probiotic supplement capsule',
    '다이어트':         'fitness diet wellness',
}

_TECH_TITLE_STOP = {
    # 한글 불용어
    '비교', '가이드', '선택법', '선택', '정리', '차이', '설치', '방법', '활용', '기능',
    '해설', '완전', '기초', '무엇', '있나', '뭘까', '어떻게', '이란', '총정리', '대응법',
    'vs', '대비',
    # 영어 불용어
    'the', 'and', 'for', 'with', 'pro', 'guide', 'tech', 'what', 'how', 'why',
}


def _tech_image_query(title: str, slug: str) -> str:
    """제목/슬러그 키워드로 적절한 Pixabay 쿼리 반환.

    매핑 미스 시 제목 앞쪽 의미 있는 단어 2개로 동적 쿼리 생성 ('중성 폴백' 보다
    주제에 가까운 이미지 확률이 높아짐).
    """
    text = (title + ' ' + slug).lower()
    for keyword, query in _TECH_IMAGE_QUERIES.items():
        if keyword.lower() in text:
            return query

    # 제목 기반 폴백 — 영어 단어 우선 (한글 쿼리는 Pixabay 태그 검증 불가 → 탈락)
    en_words = re.findall(r'[a-zA-Z]{3,}', title)
    en_words = [w for w in en_words if w.lower() not in _TECH_TITLE_STOP]
    if en_words:
        fallback = ' '.join(en_words[:3])
        log.warning(f'[이미지 매핑 미스] title={title!r} — 영어 폴백: {fallback!r}')
        return fallback

    log.warning(f'[이미지 매핑 미스] title={title!r} — 매핑 없음, 탈락')
    return ''  # 빈 쿼리 → 태그 검증 0건 → 해당 주제 탈락


def _title_matches_weak(url: str, title: str, slug: str) -> bool:
    """기술·트렌드 글의 이미지 약한 검증.
    제목/슬러그에서 추출한 유의미 토큰이 URL 에 1개라도 포함되면 통과.
    """
    hay    = url.lower()
    tokens = re.findall(r'[가-힣a-zA-Z0-9]{2,}', (title + ' ' + slug).lower())
    tokens = [t for t in tokens if t not in _TECH_TITLE_STOP]
    return any(t in hay for t in tokens) if tokens else False


_PIXABAY_NOISE_WORDS = {
    'and', 'for', 'the', 'with', 'from', 'home', 'modern',
    'wall', 'mounted', 'countertop', 'wrist', 'style',
}


def _build_tech_vision_topic(title: str, hints: dict | None) -> str:
    """기술·트렌드 글 비전 게이트 topic 문자열 구성.

    우선순위: 첫 제품명 > 카테고리 > 키워드. 제목은 항상 포함.
    """
    parts = [title.strip()] if title else []
    if isinstance(hints, dict):
        products = hints.get('products') or []
        if products:
            parts.append(f'(subject: {products[0]})')
        else:
            cat = (hints.get('category') or '').strip()
            if cat:
                parts.append(f'(category: {cat})')
            else:
                kws = hints.get('keywords') or []
                if kws:
                    parts.append(f'(keywords: {", ".join(kws[:3])})')
    return ' '.join(parts).strip()


def _iter_image_urls_tech(title: str, slug: str, hints: dict | None = None):
    """기술·트렌드 글 이미지 후보 URL 을 우선순위 순으로 yield.

    hints (옵션, content_generator 가 Claude 로부터 받은 이미지 메타데이터):
      {"products": ["Apple AirTag", ...], "keywords": ["bluetooth tracker", ...], "category": "tracker"}

    0) hints.products → Wikipedia 제품 페이지 썸네일 (제품 특정 이미지 최우선)
    0') hints.products → 웹검색 og:image (Wikipedia 미스 시)
    0") hints.keywords[0] → Pixabay 검색 + 단어 태그 검증
    1) 기존: fetch_web_image_url(title) + 제목 약한 검증
    2) 기존: _tech_image_query 매핑 기반 Pixabay 태그 검증

    검증 실패 누적 시 yield 없이 끝 → 호출측 업로드 실패, 큐 필터에선 탈락.
    """
    hints = hints or {}
    products = hints.get('products') or []
    hint_kws = hints.get('keywords') or []

    # ── 0. hints.products → Wikipedia 직접 검색 (최상 품질)
    for product_name in products[:3]:
        wiki_img = _wikipedia_image(product_name)
        if wiki_img:
            log.info(f'[tech 0a] hints→Wikipedia: {product_name!r} → {wiki_img[:60]}')
            yield wiki_img

    # ── 0'. hints.products → DDG og:image (Wikipedia 미스 대비)
    for product_name in products[:2]:
        for url in _ddg_search_urls(f'{product_name} official', limit=2):
            og = _extract_og_image(url)
            if og and _is_usable_image(og):
                log.info(f'[tech 0b] hints→og: {product_name!r} → {og[:60]}')
                yield og
                break

    # ── 0". hints.keywords → Pixabay + 키워드 태그 검증
    for kw in hint_kws[:2]:
        kw_words = [w for w in re.findall(r'[a-z]+', kw.lower())
                    if len(w) >= 3 and w not in _PIXABAY_NOISE_WORDS]
        if not kw_words:
            continue
        try:
            r = requests.get(
                'https://pixabay.com/api/',
                params={'key': PIXABAY_KEY, 'q': kw, 'image_type': 'photo',
                        'orientation': 'horizontal', 'per_page': 30, 'safesearch': 'true'},
                timeout=10,
            )
            hits = r.json().get('hits', [])
        except Exception as e:
            log.warning(f'[tech 0c] hints Pixabay 실패 ({kw!r}): {e}')
            continue
        matched = [h for h in hits
                   if any(w in (h.get('tags') or '').lower() for w in kw_words)]
        if matched:
            log.info(f'[tech 0c] hints→Pixabay: {kw!r} {len(matched)}/{len(hits)} 통과')
            for hit in _random.sample(matched, min(3, len(matched))):
                url = hit.get('webformatURL', '')
                if url:
                    yield url

    img = fetch_web_image_url(title, '')
    if img and _title_matches_weak(img, title, slug):
        log.info(f'[tech 1/2] 웹검색 검증 통과: {title[:40]}')
        yield img
    elif img:
        log.warning(f'[tech] 웹 이미지 검증 실패, 다음 폴백: {title[:40]}')

    query = _tech_image_query(title, slug)
    query_words = [
        w for w in re.findall(r'[a-z]+', query.lower())
        if len(w) >= 3 and w not in _PIXABAY_NOISE_WORDS
    ]
    if not query or not query_words:
        log.warning(f'[tech] 검증 가능한 영어 쿼리 없음 — 탈락 (title={title[:40]!r})')
        return
    try:
        r = requests.get(
            'https://pixabay.com/api/',
            params={'key': PIXABAY_KEY, 'q': query, 'image_type': 'photo',
                    'orientation': 'horizontal', 'per_page': 30, 'safesearch': 'true'},
            timeout=10,
        )
        hits = r.json().get('hits', [])
    except Exception as e:
        log.warning(f'[tech] Pixabay 실패 ({query!r}): {e}')
        return

    matched = [
        h for h in hits
        if any(w in (h.get('tags') or '').lower() for w in query_words)
    ] if query_words else hits
    if not matched:
        log.warning(f'[tech 2/2] Pixabay 태그 검증 통과 0건 — 탈락 (query={query!r})')
        return

    log.info(f'[tech 2/2] Pixabay 태그 검증: {len(matched)}/{len(hits)} 통과 (query={query!r})')
    picks = _random.sample(matched, min(5, len(matched)))
    for hit in picks:
        url = hit.get('webformatURL', '')
        if url:
            yield url


def _get_tech_image_url(title: str, slug: str) -> str:
    """첫 후보 URL만 반환 (유틸리티 호환). 발행 경로는 _iter_image_urls_tech 사용."""
    for url in _iter_image_urls_tech(title, slug):
        return url
    return ''


def has_image_candidate_product(product: dict) -> bool:
    """큐 Dry-Run 용: 이미지 후보가 1개라도 나오면 True. 업로드는 하지 않음.

    D1' 필터에서 본문 생성 전에 호출. 이 함수가 False 면 해당 제품은
    "매칭 실패"로 큐에서 제외되고 catalog 에 남음 → 다음 드로우에서 재시도.
    """
    for _ in _iter_image_urls_product(product):
        return True
    return False


def has_image_candidate_tech(title: str, slug: str, hints: dict | None = None) -> bool:
    """큐 Dry-Run 용: 기술·트렌드 글 이미지 후보 존재 여부."""
    for _ in _iter_image_urls_tech(title, slug, hints):
        return True
    return False


def _get_or_create_tags(tag_names: list[str]) -> list[int]:
    """태그명 목록 → WP 태그 ID 목록."""
    ids = []
    for name in tag_names:
        if not name.strip():
            continue
        try:
            ids.append(get_or_create_term(name.strip(), 'tags'))
        except Exception:
            pass
    return ids


def publish_spec_post(product: dict, content_html: str) -> str:
    """product CPT로 스펙 분석 글 발행. 반환: 발행 URL"""
    type_id  = get_or_create_term(product['category'], 'device_type')

    media_id = _upload_first_ok(
        _iter_image_urls_product(product),
        alt_text=product['model'],
        filename_base=product['slug'],
        vision_topic=f"{product['brand']} {product['model']} ({product['category']})",
    )

    # 태그: 브랜드 + 카테고리 한글명
    _cat_kr = {
        'smartphone':'스마트폰','laptop':'노트북','tablet':'태블릿',
        'earphone':'이어폰','smartwatch':'스마트워치','tv':'TV',
        'monitor':'모니터','camera':'카메라','gaming_console':'게임콘솔',
        'speaker':'스피커','refrigerator':'냉장고','washing_machine':'세탁기',
        'air_conditioner':'에어컨','air_purifier':'공기청정기',
        'robot_vacuum':'로봇청소기','vacuum':'청소기','microwave':'전자레인지',
        'hair_dryer':'헤어드라이어','electric_shaver':'전기면도기',
        'food_processor':'음식물처리기',
    }
    tag_names = [product['brand'], _cat_kr.get(product['category'], product['category']), '스펙분석']
    tag_ids   = _get_or_create_tags(tag_names)

    payload = {
        'title':       product['model'],
        'slug':        product['slug'],
        'content':     content_html,
        'status':      'publish',
        'device_type': [type_id],
        'tags':        tag_ids,
        'meta': {
            '_specs':        product['specs'],
            '_release_year': product.get('release_year', ''),
        },
    }
    if media_id:
        payload['featured_media'] = media_id

    r = requests.post(_api('products'), json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    link = r.json().get('link', '')
    _indexnow_ping(link)
    return link


def publish_tech_post(title: str, slug: str, content_html: str,
                      image_hints: dict | None = None) -> str:
    """기술정보 일반 포스트 발행."""
    cat_id = get_or_create_term('기술정보', 'categories')

    media_id = _upload_first_ok(
        _iter_image_urls_tech(title, slug, image_hints),
        alt_text=title,
        filename_base=slug,
        vision_topic=_build_tech_vision_topic(title, image_hints),
    )

    # 제목에서 2~3개 핵심어 태그 추출 (괄호·특수문자 제거)
    words = re.sub(r'[^\w\s가-힣]', ' ', title).split()
    tag_names = [w for w in words if len(w) >= 2][:3] + ['기술정보']
    tag_ids   = _get_or_create_tags(tag_names)

    payload = {
        'title':      title,
        'slug':       slug,
        'content':    content_html,
        'status':     'publish',
        'categories': [cat_id],
        'tags':       tag_ids,
    }
    if media_id:
        payload['featured_media'] = media_id

    r = requests.post(_api('posts'), json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    link = r.json().get('link', '')
    _indexnow_ping(link)
    return link


def publish_trend_post(title: str, slug: str, content_html: str,
                       is_hot: bool = False,
                       image_hints: dict | None = None) -> tuple[str, int]:
    """트렌드 카테고리 포스트 발행. is_hot=True 일 때 '인기' 태그 + sticky=True.

    Returns: (url, post_id)
    """
    # 카테고리 slug='trend' 조회, 없으면 생성
    r = requests.get(_api('categories'), params={'slug': 'trend'}, headers=HEADERS, timeout=10)
    items = r.json()
    if isinstance(items, list) and items:
        cat_id = items[0]['id']
    else:
        r = requests.post(_api('categories'),
                          json={'name': '트렌드', 'slug': 'trend'},
                          headers=HEADERS, timeout=10)
        cat_id = r.json().get('id', 0)

    media_id = _upload_first_ok(
        _iter_image_urls_tech(title, slug, image_hints),
        alt_text=title,
        filename_base=slug,
        vision_topic=_build_tech_vision_topic(title, image_hints),
    )

    words = re.sub(r'[^\w\s가-힣]', ' ', title).split()
    tag_names = [w for w in words if len(w) >= 2][:3] + ['트렌드']
    if is_hot:
        tag_names.append('인기')
    tag_ids = _get_or_create_tags(tag_names)

    payload = {
        'title':      title,
        'slug':       slug,
        'content':    content_html,
        'status':     'publish',
        'categories': [cat_id],
        'tags':       tag_ids,
    }
    if media_id:
        payload['featured_media'] = media_id
    if is_hot:
        payload['sticky'] = True

    r = requests.post(_api('posts'), json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    link    = data.get('link', '')
    post_id = int(data.get('id', 0))
    _indexnow_ping(link)
    return link, post_id


def post_exists(slug: str, post_type: str = 'posts') -> bool:
    """슬러그 중복 확인."""
    r = requests.get(_api(post_type), params={'slug': slug}, headers=HEADERS, timeout=10)
    items = r.json()
    return isinstance(items, list) and len(items) > 0
