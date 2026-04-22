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

# 기술 주제 키워드 → Pixabay 이미지 쿼리 매핑
_TECH_IMAGE_QUERIES = {
    'oled': 'OLED display screen',
    'amoled': 'OLED display screen',
    '디스플레이': 'display screen technology',
    '주사율': 'gaming monitor display',
    'ltpo': 'smartwatch display',
    '배터리': 'battery charging technology',
    '충전': 'wireless charging',
    '5g': '5G network mobile',
    'wifi': 'wifi router network',
    '블루투스': 'bluetooth wireless',
    'usb': 'USB cable connector',
    '프로세서': 'computer processor chip',
    '칩': 'semiconductor chip',
    'cpu': 'computer processor',
    'gpu': 'graphics card GPU',
    'ram': 'computer memory RAM',
    '카메라': 'camera lens photography',
    '센서': 'camera sensor photography',
    '화소': 'camera photography',
    '손떨림': 'camera stabilization',
    '노이즈': 'audio sound wave',
    'anc': 'headphones noise cancelling',
    '공간음향': 'spatial audio headphones',
    '돌비': 'home theater audio',
    'hdr': 'HDR display television',
    '냉각': 'cooling fan heat',
    '방열': 'cooling technology',
    '방수': 'waterproof electronics',
    '재활용': 'recycling sustainability green',
    '친환경': 'eco friendly sustainable green',
    '에너지': 'energy efficiency solar',
    '인버터': 'air conditioner inverter',
    '필터': 'air filter purifier',
    '흡입': 'vacuum cleaner',
    '로봇': 'robot vacuum smart home',
    '세탁': 'washing machine laundry',
    '냉장': 'refrigerator kitchen',
    '헤어': 'hair dryer beauty',
    '면도': 'electric shaver grooming',
    '음식물': 'food waste kitchen',
    '전자레인지': 'microwave oven kitchen',
}

import random as _random

def _tech_image_query(title: str, slug: str) -> str:
    """제목/슬러그 키워드로 적절한 Pixabay 쿼리 반환."""
    text = (title + ' ' + slug).lower()
    for keyword, query in _TECH_IMAGE_QUERIES.items():
        if keyword in text:
            return query
    return 'technology gadget modern'


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

    media_id = 0
    img_url  = _get_image_url(product)
    if img_url:
        media_id = upload_image_from_url(img_url, product['model'])

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
    return r.json().get('link', '')


def publish_tech_post(title: str, slug: str, content_html: str) -> str:
    """기술정보 일반 포스트 발행."""
    cat_id = get_or_create_term('기술정보', 'categories')

    # 주제별 이미지 쿼리
    media_id = 0
    query = _tech_image_query(title, slug)
    try:
        r = requests.get(
            'https://pixabay.com/api/',
            params={'key': PIXABAY_KEY, 'q': query, 'image_type': 'photo',
                    'orientation': 'horizontal', 'per_page': 10, 'safesearch': 'true'},
            timeout=10,
        )
        hits = r.json().get('hits', [])
        if hits:
            img_url  = _random.choice(hits).get('webformatURL', '')
            media_id = upload_image_from_url(img_url, slug)
    except Exception:
        pass

    # 제목에서 2~3개 핵심어 태그 추출 (괄호·특수문자 제거)
    import re as _re
    words = _re.sub(r'[^\w\s가-힣]', ' ', title).split()
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
    return r.json().get('link', '')


def publish_trend_post(title: str, slug: str, content_html: str) -> str:
    """트렌드 카테고리 포스트 발행."""
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

    media_id = 0
    query = _tech_image_query(title, slug)
    try:
        r = requests.get(
            'https://pixabay.com/api/',
            params={'key': PIXABAY_KEY, 'q': query, 'image_type': 'photo',
                    'orientation': 'horizontal', 'per_page': 10, 'safesearch': 'true'},
            timeout=10,
        )
        hits = r.json().get('hits', [])
        if hits:
            img_url  = _random.choice(hits).get('webformatURL', '')
            media_id = upload_image_from_url(img_url, slug)
    except Exception:
        pass

    import re as _re
    words = _re.sub(r'[^\w\s가-힣]', ' ', title).split()
    tag_names = [w for w in words if len(w) >= 2][:3] + ['트렌드']
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
    return r.json().get('link', '')


def post_exists(slug: str, post_type: str = 'posts') -> bool:
    """슬러그 중복 확인."""
    r = requests.get(_api(post_type), params={'slug': slug}, headers=HEADERS, timeout=10)
    items = r.json()
    return isinstance(items, list) and len(items) > 0
