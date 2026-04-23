"""특정 WordPress 포스트의 featured_media를 현재 이미지 로직으로 재생성.

사용: python3 replace_post_image.py <post_id>
"""
import sys
import requests
import wp_publisher as wp


def main(post_id: int) -> None:
    # 1. 포스트 조회
    r = requests.get(wp._api(f'posts/{post_id}'), headers=wp.HEADERS, timeout=15)
    r.raise_for_status()
    post = r.json()
    title = post.get('title', {}).get('rendered', '')
    slug  = post.get('slug', '')
    old_media = post.get('featured_media', 0)
    print(f'[post #{post_id}] title={title!r} slug={slug!r} old_media={old_media}')

    # HTML entity 복원 (에어컨 ⇒ 에어컨)
    import html
    title = html.unescape(title)

    # 2. 이미지 재생성 (publish_tech_post와 동일 로직)
    img_url = wp.fetch_web_image_url(title, '')
    src = '웹검색'
    if not img_url:
        query = wp._tech_image_query(title, slug)
        print(f'  웹검색 실패 → Pixabay 쿼리={query!r}')
        r = requests.get(
            'https://pixabay.com/api/',
            params={'key': wp.PIXABAY_KEY, 'q': query, 'image_type': 'photo',
                    'orientation': 'horizontal', 'per_page': 10, 'safesearch': 'true'},
            timeout=10,
        )
        hits = r.json().get('hits', [])
        if hits:
            import random
            img_url = random.choice(hits).get('webformatURL', '')
            src = f'Pixabay({query})'
    if not img_url:
        print('이미지 획득 실패', file=sys.stderr)
        sys.exit(1)
    print(f'  이미지 소스={src}: {img_url[:100]}')

    # 3. 업로드
    new_media = wp.upload_image_from_url(img_url, slug)
    if not new_media:
        print('업로드 실패', file=sys.stderr)
        sys.exit(1)
    print(f'  신규 media_id={new_media}')

    # 4. featured_media 갱신
    r = requests.post(wp._api(f'posts/{post_id}'),
                      json={'featured_media': new_media},
                      headers=wp.HEADERS, timeout=15)
    r.raise_for_status()
    print(f'  featured_media 갱신 완료: {old_media} → {new_media}')

    # 5. 구 미디어 삭제 (force=true)
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
