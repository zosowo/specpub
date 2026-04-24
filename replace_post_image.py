"""특정 WordPress 포스트의 featured_media를 현재 이미지 로직으로 재생성.

사용: python3 replace_post_image.py <post_id>

post_type='product' 인 경우 catalog.PRODUCTS 에서 slug 로 조회해
`_iter_image_urls_product` (catalog_images 매핑 우선) 경로를 사용.
일반 post 는 `_iter_image_urls_tech` 경로.
"""
import html
import sys
import requests
import wp_publisher as wp


def main(post_id: int) -> None:
    r = requests.get(wp._api(f'posts/{post_id}'), headers=wp.HEADERS, timeout=15)
    if r.status_code == 404:
        r = requests.get(wp._api(f'products/{post_id}'), headers=wp.HEADERS, timeout=15)
    r.raise_for_status()
    post = r.json()

    title = html.unescape(post.get('title', {}).get('rendered', ''))
    slug  = post.get('slug', '')
    post_type = post.get('type', 'post')
    old_media = post.get('featured_media', 0)
    print(f'[#{post_id}] type={post_type} slug={slug!r} old_media={old_media}')

    if post_type == 'product':
        from catalog import PRODUCTS
        product = next((p for p in PRODUCTS if p.get('slug') == slug), None)
        if not product:
            print(f'catalog 에 slug={slug!r} 없음 — tech 경로로 폴백', file=sys.stderr)
            url_iter = wp._iter_image_urls_tech(title, slug)
            vision_topic = title
        else:
            url_iter = wp._iter_image_urls_product(product)
            vision_topic = f"{product['brand']} {product['model']} ({product['category']})"
    else:
        url_iter = wp._iter_image_urls_tech(title, slug)
        vision_topic = title

    new_media = wp._upload_first_ok(
        url_iter,
        alt_text=title,
        filename_base=slug,
        vision_topic=vision_topic,
    )
    if not new_media:
        print('이미지 획득/업로드 실패', file=sys.stderr)
        sys.exit(1)
    print(f'  신규 media_id={new_media}')

    endpoint = 'products' if post_type == 'product' else 'posts'
    r = requests.post(wp._api(f'{endpoint}/{post_id}'),
                      json={'featured_media': new_media},
                      headers=wp.HEADERS, timeout=15)
    r.raise_for_status()
    print(f'  featured_media 갱신 완료: {old_media} → {new_media}')

    if old_media:
        r = requests.delete(wp._api(f'media/{old_media}'),
                            params={'force': 'true'},
                            headers=wp.HEADERS, timeout=15)
        print(f'  구 media #{old_media} 삭제: {r.status_code}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('사용법: python3 replace_post_image.py <post_id>', file=sys.stderr)
        sys.exit(2)
    main(int(sys.argv[1]))
