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


def _api(path: str) -> str:
    return f'{WP_URL}/wp-json/wp/v2/{path}'


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
    'microwave':      'microwave oven kitchen',
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
    """Pixabay 폴백 이미지 검색."""
    brand    = product.get('brand', '')
    category = product.get('category', 'smartphone')

    queries = [
        f"{brand} {_CATEGORY_QUERIES.get(category, 'technology')}",
        _CATEGORY_QUERIES.get(category, 'technology'),
        'technology gadget',
    ]

    for query in queries:
        try:
            r = requests.get(
                'https://pixabay.com/api/',
                params={
                    'key':         PIXABAY_KEY,
                    'q':           query,
                    'image_type':  'photo',
                    'orientation': 'horizontal',
                    'category':    'technology',
                    'min_width':   400,
                    'per_page':    10,
                    'safesearch':  'true',
                },
                timeout=10,
            )
            hits = r.json().get('hits', [])
            if hits:
                return hits[0].get('webformatURL', '')
        except Exception as e:
            log.warning(f'Pixabay 검색 실패 ({query}): {e}')
    return ''


def _get_image_url(product: dict) -> str:
    """우선순위: 웹 검색 → Pixabay → Unsplash."""
    model    = product.get('model', '')
    brand    = product.get('brand', '')
    category = product.get('category', 'smartphone')

    img = fetch_web_image_url(model, brand)
    if img:
        return img

    log.info(f'웹 이미지 없음, Pixabay 폴백: {model}')
    img = fetch_pixabay_image_url(product)
    if img:
        return img

    log.info(f'Pixabay 없음, Unsplash 폴백: {model}')
    return _fetch_unsplash_image(category)


# ──────────────────────────────────────────────────────────
# WordPress 미디어 업로드
# ──────────────────────────────────────────────────────────

def upload_image_from_url(image_url: str, alt_text: str = '') -> int:
    """이미지 URL을 WP 미디어 라이브러리에 업로드, media ID 반환."""
    try:
        img_r = requests.get(image_url, headers={'User-Agent': _UA}, timeout=15)
        img_r.raise_for_status()
        img_data = img_r.content

        ext = image_url.split('?')[0].rsplit('.', 1)[-1].lower()
        if ext not in ('jpg', 'jpeg', 'png', 'webp'):
            ext = 'jpg'
        mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                'png': 'image/png', 'webp': 'image/webp'}.get(ext, 'image/jpeg')

        safe_name = re.sub(r'[^\x00-\x7F]', '', alt_text)  # ASCII만 남기기
        safe_name = re.sub(r'[^\w\-]', '_', safe_name)[:60] or 'image'
        headers = {
            'Authorization':       HEADERS['Authorization'],
            'Content-Type':        mime,
            'Content-Disposition': f'attachment; filename="{safe_name}.{ext}"',
        }
        r = requests.post(_api('media'), data=img_data, headers=headers, timeout=30)
        if r.status_code in (200, 201):
            media_id = r.json().get('id', 0)
            log.info(f'이미지 업로드 성공: media_id={media_id}')
            return media_id
        log.warning(f'이미지 업로드 실패: {r.status_code}')
    except Exception as e:
        log.warning(f'이미지 업로드 오류: {e}')
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

def publish_spec_post(product: dict, content_html: str) -> str:
    """product CPT로 스펙 분석 글 발행. 반환: 발행 URL"""
    type_id  = get_or_create_term(product['category'], 'device_type')

    # 웹 검색 → Pixabay 순서로 이미지 확보
    media_id = 0
    img_url  = _get_image_url(product)
    if img_url:
        media_id = upload_image_from_url(img_url, product['model'])

    payload = {
        'title':       product['model'],
        'slug':        product['slug'],
        'content':     content_html,
        'status':      'publish',
        'device_type': [type_id],
        'meta': {
            '_specs':        product['specs'],
            '_release_year': product.get('release_year', ''),
        },
    }
    if media_id:
        payload['featured_media'] = media_id

    r = requests.post(_api('products'), json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json().get('link', '')


def publish_tech_post(title: str, slug: str, content_html: str) -> str:
    """기술정보 일반 포스트 발행."""
    cat_id = get_or_create_term('기술정보', 'categories')

    # 기술 글: technology 일반 이미지 (Pixabay만으로 충분)
    media_id = 0
    tech_product = {'brand': '', 'category': 'smartphone', 'model': slug}
    try:
        import random
        r = requests.get(
            'https://pixabay.com/api/',
            params={'key': PIXABAY_KEY, 'q': 'technology', 'image_type': 'photo',
                    'orientation': 'horizontal', 'per_page': 10, 'safesearch': 'true'},
            timeout=10,
        )
        hits = r.json().get('hits', [])
        if hits:
            img_url  = random.choice(hits).get('webformatURL', '')
            media_id = upload_image_from_url(img_url, slug)
    except Exception:
        pass

    payload = {
        'title':      title,
        'slug':       slug,
        'content':    content_html,
        'status':     'publish',
        'categories': [cat_id],
    }
    if media_id:
        payload['featured_media'] = media_id

    r = requests.post(_api('posts'), json=payload, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json().get('link', '')


def post_exists(slug: str, post_type: str = 'posts') -> bool:
    """슬러그 중복 확인."""
    r = requests.get(_api(post_type), params={'slug': slug}, headers=HEADERS, timeout=10)
    items = r.json()
    return isinstance(items, list) and len(items) > 0
