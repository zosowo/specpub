"""기존 발행된 포스트/제품 URL을 IndexNow API로 일괄 재제출.

- `wp_publisher._indexnow_ping` 는 신규 발행 시 1건씩 쏜다.
- 이 스크립트는 이미 발행된 모든 글을 한 번에 쏘는 초기 동기화용.
- IndexNow 는 최대 10,000 URL/요청 허용 (POST JSON).

사용:
    python3 indexnow_resubmit.py
"""
import os
import sys
import json
import subprocess
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

KEY    = os.getenv('INDEXNOW_KEY', '').strip()
WP_DIR = '/home/zosowo/blog'

if not KEY:
    sys.exit('INDEXNOW_KEY 가 .env 에 없습니다.')


def _wp_urls() -> list[str]:
    out = subprocess.check_output(
        ['wp', 'post', 'list',
         '--post_status=publish',
         '--post_type=post,product',
         '--fields=url',
         '--format=json',
         '--posts_per_page=-1',
         f'--path={WP_DIR}'],
        text=True,
    )
    return [row['url'] for row in json.loads(out) if row.get('url')]


def main() -> None:
    urls = _wp_urls()
    if not urls:
        print('발행된 글이 없습니다.')
        return

    host = urlparse(urls[0]).hostname
    payload = {
        'host':        host,
        'key':         KEY,
        'keyLocation': f'https://{host}/{KEY}.txt',
        'urlList':     urls,
    }

    r = requests.post(
        'https://api.indexnow.org/indexnow',
        json=payload,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        timeout=20,
    )
    print(f'HTTP {r.status_code} | URL {len(urls)}건 전송 | host={host}')
    if r.status_code not in (200, 202):
        print(r.text[:400])


if __name__ == '__main__':
    main()
