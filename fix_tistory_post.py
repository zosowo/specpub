"""
특정 티스토리 글의 본문·제목·태그를 재생성 유틸 (수동 실행).

사용:
  python3 fix_tistory_post.py <post_id>

tistory_published.json 에서 해당 post_id 의 seed keyword / category 조회
 → tistory_generator.generate_post_json() 으로 본문 재생성
 → tistory_publisher.publish_post(post_id=...) 로 업데이트.
"""
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

BASE = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE, '.env'))
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

import tistory_generator as gen
import tistory_publisher as pub
import telegram_utils as tg

HISTORY_FILE = os.path.join(BASE, 'tistory_published.json')
KST = timezone(timedelta(hours=9))


def _find_record(post_id: int) -> dict | None:
    if not os.path.exists(HISTORY_FILE):
        return None
    try:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    except Exception:
        return None
    for rec in reversed(history):
        url = rec.get('url', '')
        if url.endswith(f'/{post_id}') or f'/entry/{post_id}' in url or f'/entry/' in url and url.rstrip('/').endswith(str(post_id)):
            return rec
    return None


def main(post_id: int):
    rec = _find_record(post_id)
    if not rec:
        log.error(f'#{post_id} 이력 없음 — tistory_published.json 확인')
        sys.exit(1)

    kw       = rec.get('keyword') or rec.get('title', '')
    category = rec.get('category', 'guide')
    log.info(f'[fix] 대상 #{post_id}: seed={kw!r}, cat={category}')

    out = gen.generate_post_json(kw, related=[], category=category)
    if not out or not out.get('body_html'):
        log.error('본문 재생성 실패')
        sys.exit(2)

    title = out.get('title') or rec.get('title')

    # 이미지 재소싱 (선택)
    img_url = gen.fetch_image_url(out.get('image_query', ''), title)
    if img_url:
        body = f'<p><img src="{img_url}" alt="{title}" loading="lazy"></p>' + out['body_html']
    else:
        body = out['body_html']

    t0 = time.time()
    url = pub.publish_post(
        title=title,
        html_body=body,
        tags=out.get('tags') or rec.get('tags') or [],
        visibility='public',
        category_name=os.getenv('TISTORY_CATEGORY_NAME', 'Note'),
        post_id=post_id,
    )
    elapsed = time.time() - t0
    log.info(f'[fix] #{post_id} 업데이트 완료 ({elapsed:.1f}s) → {url}')

    tg.send(
        f'🛠️ *글 복구 완료* #{post_id} ({elapsed:.1f}s)\n\n'
        f'📝 {title[:80]}\n'
        f'🔗 https://dwang.tistory.com/{post_id}',
        source='Tistory',
    )


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('사용법: python3 fix_tistory_post.py <post_id>', file=sys.stderr)
        sys.exit(2)
    main(int(sys.argv[1]))
