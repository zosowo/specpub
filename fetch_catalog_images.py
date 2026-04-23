"""catalog.py 의 제품별 공식 이미지 URL을 자동 수집하여
`catalog_images.py` 에 slug → URL 매핑으로 저장.

수집 전략:
  1. Wikipedia REST API summary.originalimage (제목 매칭 확인)
  2. 브랜드 공식 사이트 검색 (DDG site: 필터) → og:image
  3. DDG 웹 검색(일반) → og:image

각 후보는 `wp_publisher._image_matches` 로 제품명 토큰 매칭 검증 통과 시에만 채택.
누락된 제품은 stdout + 텔레그램으로 리포트.

사용:
    python3 fetch_catalog_images.py [--dry-run]
"""
import os
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from catalog import PRODUCTS
from wp_publisher import (
    _image_matches,
    _is_usable_image,
    _wikipedia_image,
    _ddg_search_urls,
    _extract_og_image,
    _BRAND_SITES,
)

try:
    from catalog_images import CATALOG_IMAGES as _EXISTING
except ImportError:
    _EXISTING = {}

try:
    from telegram_utils import send as tg_send
except ImportError:
    def tg_send(_: str) -> None: pass


IMAGES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'catalog_images.py')


def _pick_image(brand: str, model: str) -> str:
    """여러 소스 순회, 엄격 URL 매칭 검증 통과한 첫 이미지 URL 반환.

    검증은 이미지 URL 만으로 수행 (context/query 우회 금지).
    """
    query = model if model.lower().startswith(brand.lower()) else f'{brand} {model}'

    # 1. Wikipedia
    img = _wikipedia_image(query, brand)
    if img and _is_usable_image(img) and _image_matches(img, brand, model):
        return img

    # 2. 브랜드 공식 사이트 + 3. 일반 검색
    searches = []
    site = _BRAND_SITES.get(brand)
    if site:
        searches.append(f'{query} site:{site}')
    searches.append(f'{query} official product')

    for q in searches:
        for url in _ddg_search_urls(q, limit=5):
            og = _extract_og_image(url)
            if og and _is_usable_image(og) and _image_matches(og, brand, model):
                return og

    return ''


def _write_images_file(mapping: dict) -> None:
    lines = [
        '"""catalog.py 제품별 공식 이미지 URL (slug → URL).',
        '',
        'fetch_catalog_images.py 가 자동 생성/갱신. Wikipedia/브랜드 공식 사이트 기반,',
        'wp_publisher._image_matches 검증 통과 URL만 포함.',
        '"""',
        '',
        'CATALOG_IMAGES = {',
    ]
    for slug in sorted(mapping):
        url = mapping[slug].replace('"', '\\"')
        lines.append(f'    "{slug}": "{url}",')
    lines.append('}')
    content = '\n'.join(lines) + '\n'

    tmp = IMAGES_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(content)
    # 문법 검증
    import ast
    ast.parse(content)
    os.replace(tmp, IMAGES_PATH)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--only-missing', action='store_true', help='기존 매핑에 없는 slug만 시도')
    args = ap.parse_args()

    mapping = dict(_EXISTING)
    tried = 0
    found = 0
    missed = []

    for p in PRODUCTS:
        slug = p['slug']
        if args.only_missing and slug in mapping:
            continue
        tried += 1
        url = _pick_image(p['brand'], p['model'])
        if url:
            mapping[slug] = url
            found += 1
            print(f'  ✓ {slug}')
        else:
            missed.append(f"{p['brand']} {p['model']} ({slug})")
            print(f'  ✗ {slug}  — 실패')
        time.sleep(0.3)  # API rate 보호

    print(f'\n요약: {tried}개 시도 / {found}개 성공 / {len(missed)}개 실패')
    print(f'총 매핑 수: {len(mapping)}')

    if not args.dry_run:
        _write_images_file(mapping)
        print(f'저장: {IMAGES_PATH}')

    if missed:
        body = '⚠️ 이미지 수집 실패 제품:\n' + '\n'.join(f'- {m}' for m in missed[:30])
        if len(missed) > 30:
            body += f'\n(외 {len(missed) - 30}개)'
        tg_send(body)


if __name__ == '__main__':
    main()
