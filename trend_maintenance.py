"""
트렌드 '인기' 태그 + 상단 고정(sticky) 만료 관리 — 매일 06:00.

keyword_history.json 의 pin_expiry 가 오늘 이전인 post_id 를 찾아:
  - sticky=False
  - '인기' 태그 제거
그 후 pin_expiry / post_id 필드 정리.

크론: 0 6 * * * TZ=Asia/Seoul /usr/bin/python3 /home/zosowo/specpub/trend_maintenance.py
      >> /home/zosowo/specpub/trend.log 2>&1
"""
import os
import json
import logging
from datetime import date
from dotenv import load_dotenv

import requests

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

from trend_generator import KW_HIST_F
from wp_publisher import _api, HEADERS


def _get_hot_tag_id() -> int:
    try:
        r = requests.get(_api('tags'), params={'slug': '인기'}, headers=HEADERS, timeout=10)
        items = r.json()
        if isinstance(items, list) and items:
            return int(items[0]['id'])
    except Exception as e:
        log.warning(f"'인기' 태그 조회 실패: {e}")
    return 0


def _expire_post(post_id: int, hot_tag_id: int):
    """해당 포스트 sticky 해제 + '인기' 태그 제거."""
    try:
        r = requests.get(f"{_api('posts')}/{post_id}", headers=HEADERS, timeout=10)
        post = r.json()
        if not isinstance(post, dict) or 'id' not in post:
            log.warning(f'post_id={post_id} 조회 실패 또는 삭제됨')
            return False
        tags = post.get('tags', []) or []
        if hot_tag_id and hot_tag_id in tags:
            tags = [t for t in tags if t != hot_tag_id]
        r = requests.post(
            f"{_api('posts')}/{post_id}",
            json={'sticky': False, 'tags': tags},
            headers=HEADERS, timeout=15,
        )
        r.raise_for_status()
        log.info(f'만료 처리 완료: post_id={post_id}')
        return True
    except Exception as e:
        log.error(f'만료 처리 실패 post_id={post_id}: {e}')
        return False


def run():
    if not os.path.exists(KW_HIST_F):
        log.info('keyword_history.json 없음 — 종료')
        return 0

    with open(KW_HIST_F, encoding='utf-8') as f:
        history = json.load(f)

    today = date.today().isoformat()
    expired_post_ids = {}  # post_id -> [kw1, kw2, ...]

    for kw, info in history.items():
        expiry = info.get('pin_expiry')
        pid    = info.get('post_id')
        if expiry and pid and expiry < today:
            expired_post_ids.setdefault(pid, []).append(kw)

    if not expired_post_ids:
        log.info('만료 대상 없음')
        return 0

    hot_tag_id = _get_hot_tag_id()
    processed  = 0

    for pid, kws in expired_post_ids.items():
        if _expire_post(pid, hot_tag_id):
            processed += 1
            for kw in kws:
                history[kw].pop('pin_expiry', None)
                history[kw].pop('post_id',    None)

    tmp = KW_HIST_F + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    os.replace(tmp, KW_HIST_F)

    log.info(f'완료: {processed}/{len(expired_post_ids)} 건 처리')
    return processed


if __name__ == '__main__':
    run()
