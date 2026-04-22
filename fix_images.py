"""발행된 게시물의 누락된 이미지를 일괄 보정."""
import sys
import os
import logging
import requests

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from wp_publisher import (
    HEADERS, WP_URL, _get_image_url, upload_image_from_url,
    fetch_web_image_url, fetch_pixabay_image_url
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)


def _api(path):
    return f'{WP_URL}/wp-json/wp/v2/{path}'


def fix_post_image(post_id: int, post_type: str, model: str, brand: str, category: str = 'smartphone'):
    """단일 포스트 이미지 업데이트."""
    product = {'model': model, 'brand': brand, 'category': category}
    img_url = _get_image_url(product)
    if not img_url:
        log.warning(f'이미지 없음: {model}')
        return False

    media_id = upload_image_from_url(img_url, model)
    if not media_id:
        log.warning(f'업로드 실패: {model}')
        return False

    r = requests.patch(
        _api(f'{post_type}/{post_id}'),
        json={'featured_media': media_id},
        headers=HEADERS,
        timeout=15,
    )
    if r.status_code in (200, 201):
        log.info(f'완료: [{post_type}] id={post_id} {model} → media_id={media_id}')
        return True
    else:
        log.error(f'업데이트 실패: {r.status_code} {r.text[:100]}')
        return False


def fetch_all_posts(post_type: str) -> list:
    """이미지 없는 게시물 목록 반환."""
    items = []
    page = 1
    while True:
        r = requests.get(
            _api(post_type),
            params={'per_page': 100, 'page': page,
                    '_fields': 'id,slug,title,featured_media',
                    'status': 'publish'},
            headers=HEADERS,
            timeout=15,
        )
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        items.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return items


def guess_meta(slug: str, title: str) -> tuple[str, str, str]:
    """슬러그에서 브랜드·카테고리 추정."""
    brand_map = {
        'samsung': 'Samsung', 'apple': 'Apple', 'lg': 'LG',
        'sony': 'Sony', 'google': 'Google', 'xiaomi': 'Xiaomi',
        'asus': 'ASUS', 'lenovo': 'Lenovo', 'dell': 'Dell',
        'hp': 'HP', 'microsoft': 'Microsoft', 'oneplus': 'OnePlus',
        'motorola': 'Motorola', 'garmin': 'Garmin', 'bose': 'Bose',
        'jbl': 'JBL', 'sennheiser': 'Sennheiser', 'nothing': 'Nothing',
    }
    cat_map = {
        'laptop': 'laptop', 'macbook': 'laptop', 'gram': 'laptop',
        'galaxy-book': 'laptop', 'surface': 'laptop',
        'ipad': 'tablet', 'tab': 'tablet', 'pad': 'tablet',
        'earphone': 'earphone', 'earbuds': 'earphone', 'headphone': 'earphone',
        'airpods': 'earphone', 'buds': 'earphone', 'wh-': 'earphone',
        'watch': 'smartwatch', 'fenix': 'smartwatch', 'band': 'smartwatch',
        'galaxy-watch': 'smartwatch',
    }

    brand = 'Unknown'
    for key, val in brand_map.items():
        if key in slug:
            brand = val
            break

    category = 'smartphone'
    for key, val in cat_map.items():
        if key in slug:
            category = val
            break

    model = title.strip()
    return model, brand, category


if __name__ == '__main__':
    ok = fail = skip = 0

    for ptype in ('products', 'posts'):
        items = fetch_all_posts(ptype)
        no_img = [i for i in items if not i.get('featured_media')]
        print(f'\n[{ptype}] 전체 {len(items)}개, 이미지 없음 {len(no_img)}개')

        for item in no_img:
            pid   = item['id']
            slug  = item['slug']
            title = item['title']['rendered']
            model, brand, category = guess_meta(slug, title)

            print(f'  처리중: id={pid} {title[:50]}')
            success = fix_post_image(pid, ptype, model, brand, category)
            if success:
                ok += 1
            else:
                fail += 1

    print(f'\n완료: 성공 {ok}개 / 실패 {fail}개')
