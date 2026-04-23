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
    """Pixabay 카테고리 폴백 — 브랜드 배제, 카테고리 쿼리만 사용.

    이전에는 `f"{brand} {category}"` 조합으로 검색했으나, Pixabay 결과가
    해시형 URL 이라 검증이 어렵고 브랜드 섞이면 엉뚱한 카테고리가 매칭됨
    (예: Pixel 9 글에 노트북). 카테고리 전용 쿼리로 단순화하여 최소한
    "같은 카테고리" 보장.
    """
    category = product.get('category', 'smartphone')
    query    = _CATEGORY_QUERIES.get(category, 'technology gadget')

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
            timeout=10,
        )
        hits = r.json().get('hits', [])
        if hits:
            return _random.choice(hits).get('webformatURL', '')
    except Exception as e:
        log.warning(f'Pixabay 카테고리 폴백 실패 ({query}): {e}')
    return ''


def _iter_image_urls_product(product: dict):
    """스펙 제품 이미지 후보 URL 을 우선순위 순으로 yield.

    단계:
      1. catalog_images 매핑 (slug별 공식 URL, 100% 정확)
      2. 웹검색 (Wikipedia/DDG/og) + 토큰 검증
      3. Pixabay 카테고리 폴백 — 브랜드 배제
      4. Unsplash 카테고리 폴백 — 최후 안전망

    호출측은 업로드 성공할 때까지 순회 (Pixabay 429 등 CDN 실패 대비).
    """
    model    = product.get('model', '')
    brand    = product.get('brand', '')
    category = product.get('category', 'smartphone')
    slug     = product.get('slug', '')

    fixed = (product.get('image_url') or _CATALOG_IMAGES.get(slug, '') or '').strip()
    if fixed and _is_usable_image(fixed):
        log.info(f'[1/4] catalog image_url: {brand} {model}')
        yield fixed

    img = fetch_web_image_url(model, brand)
    if img and _image_matches(img, brand, model):
        log.info(f'[2/4] 웹검색 검증 통과: {brand} {model}')
        yield img
    elif img:
        log.warning(f'웹 이미지 검증 실패, 다음 폴백: {brand} {model}')

    img = fetch_pixabay_image_url(product)
    if img:
        log.info(f'[3/4] Pixabay 카테고리 폴백: {category}')
        yield img

    img = _fetch_unsplash_image(category)
    if img:
        log.info(f'[4/4] Unsplash 카테고리 폴백: {category}')
        yield img


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


def _upload_first_ok(url_iter, alt_text: str = '', filename_base: str = '') -> int:
    """후보 URL 순회하며 업로드 성공하는 첫 URL 의 media_id 반환.

    개별 URL 이 429/timeout/404 등으로 실패해도 다음 후보로 자동 폴백.
    모든 후보 소진 시 0 반환.
    """
    tried = 0
    for url in url_iter:
        if not url:
            continue
        tried += 1
        media_id = upload_image_from_url(url, alt_text=alt_text, filename_base=filename_base)
        if media_id:
            return media_id
        log.warning(f'[upload {tried}] 실패, 다음 후보 시도')
    if tried == 0:
        log.error('이미지 후보 없음')
    else:
        log.error(f'이미지 후보 {tried}개 모두 업로드 실패')
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
    '카메라':           'camera lens photography',
    'camera':           'camera lens photography',
    '센서':             'camera sensor photography',
    '화소':             'camera photography',
    '손떨림':           'camera stabilization',
    '미러리스':         'mirrorless camera photography',
    '게임기':           'game console controller',
    '콘솔':             'game console controller',
    'playstation':      'playstation game console',
    'xbox':             'xbox game console',
    '닌텐도':           'nintendo switch console',

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
    '공간음향':         'spatial audio headphones',
    '돌비':             'home theater audio',
    'anc':              'headphones noise cancelling',
    '노이즈':           'audio sound wave',

    # ── 효율·친환경·안전 ──
    '냉각':             'cooling fan heat',
    '방열':             'cooling technology',
    '방수':             'waterproof electronics',
    '재활용':           'recycling sustainability green',
    '친환경':           'eco friendly sustainable green',
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

    # 제목 기반 폴백
    words = re.findall(r'[가-힣a-zA-Z]{2,}', title)
    words = [w for w in words if w.lower() not in _TECH_TITLE_STOP]
    if words:
        fallback = ' '.join(words[:2])
        log.warning(f'[이미지 매핑 미스] title={title!r} — 제목 폴백: {fallback!r}')
        return fallback

    log.warning(f'[이미지 매핑 미스] title={title!r} — 중성 폴백 사용')
    return 'home electronics appliance'


def _title_matches_weak(url: str, title: str, slug: str) -> bool:
    """기술·트렌드 글의 이미지 약한 검증.
    제목/슬러그에서 추출한 유의미 토큰이 URL 에 1개라도 포함되면 통과.
    """
    hay    = url.lower()
    tokens = re.findall(r'[가-힣a-zA-Z0-9]{2,}', (title + ' ' + slug).lower())
    tokens = [t for t in tokens if t not in _TECH_TITLE_STOP]
    return any(t in hay for t in tokens) if tokens else False


def _iter_image_urls_tech(title: str, slug: str):
    """기술·트렌드 글 이미지 후보 URL 을 우선순위 순으로 yield.

    1) 웹검색 og:image + 제목 토큰 약한 검증
    2) Pixabay (_tech_image_query 매핑 또는 제목 기반)
    3) Unsplash 최후 폴백

    호출측은 업로드 성공할 때까지 순회 (Pixabay 429 등 CDN 실패 대비).
    """
    img = fetch_web_image_url(title, '')
    if img and _title_matches_weak(img, title, slug):
        log.info(f'[tech 1/3] 웹검색 검증 통과: {title[:40]}')
        yield img
    elif img:
        log.warning(f'[tech] 웹 이미지 검증 실패, 다음 폴백: {title[:40]}')

    query = _tech_image_query(title, slug)
    try:
        r = requests.get(
            'https://pixabay.com/api/',
            params={'key': PIXABAY_KEY, 'q': query, 'image_type': 'photo',
                    'orientation': 'horizontal', 'per_page': 15, 'safesearch': 'true'},
            timeout=10,
        )
        hits = r.json().get('hits', [])
        if hits:
            log.info(f'[tech 2/3] Pixabay: {query!r}')
            # 여러 후보를 무작위 순서로 yield — 한 URL 이 429여도 다음 URL 시도
            picks = _random.sample(hits, min(5, len(hits)))
            for hit in picks:
                url = hit.get('webformatURL', '')
                if url:
                    yield url
    except Exception as e:
        log.warning(f'[tech] Pixabay 실패 ({query!r}): {e}')

    img = _fetch_unsplash_image('smartphone')
    if img:
        log.info(f'[tech 3/3] Unsplash 폴백')
        yield img


def _get_tech_image_url(title: str, slug: str) -> str:
    """첫 후보 URL만 반환 (유틸리티 호환). 발행 경로는 _iter_image_urls_tech 사용."""
    for url in _iter_image_urls_tech(title, slug):
        return url
    return ''


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


def publish_tech_post(title: str, slug: str, content_html: str) -> str:
    """기술정보 일반 포스트 발행."""
    cat_id = get_or_create_term('기술정보', 'categories')

    # 이미지: 3단계 폴백 (웹검색+검증 → Pixabay → Unsplash). 각 단계 업로드 실패 시 다음 후보.
    media_id = _upload_first_ok(
        _iter_image_urls_tech(title, slug),
        alt_text=title,
        filename_base=slug,
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
                       is_hot: bool = False) -> tuple[str, int]:
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

    # 이미지: 3단계 폴백 (웹검색+검증 → Pixabay → Unsplash). 각 단계 업로드 실패 시 다음 후보.
    media_id = _upload_first_ok(
        _iter_image_urls_tech(title, slug),
        alt_text=title,
        filename_base=slug,
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
