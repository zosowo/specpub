"""
인기 태그 + sticky 만료 해제 — 매일 06:00 크론.

keyword_history.json 에서 pin_expiry 가 오늘 이전인 항목을 찾아:
  1) 해당 post_id 의 sticky=False 로 변경
  2) 포스트 태그에서 '인기' 태그 제거 (다른 태그는 유지)
  3) history 에서 post_id / pin_expiry 필드 제거 (count/score 유지)

크론: 0 6 * * * TZ=Asia/Seoul /usr/bin/python3 /home/zosowo/specpub/trend_maintenance.py
      >> /home/zosowo/specpub/trend.log 2>&1
"""
import json
import logging
import os
from datetime import date, datetime

import requests
from dotenv import load_dotenv

import telegram_utils as tg
from trend_generator import KW_HIST_F
from wp_publisher import HEADERS, _api

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

HOT_TAG_NAME = '인기'


def _load_history() -> dict:
    if not os.path.exists(KW_HIST_F):
        return {}
    try:
        with open(KW_HIST_F, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log.error(f'history 로드 실패: {e}')
        return {}


def _save_history(h: dict):
    tmp = KW_HIST_F + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(h, f, ensure_ascii=False, indent=2)
    os.replace(tmp, KW_HIST_F)


def _find_hot_tag_id() -> int:
    """'인기' 태그 ID 조회 (slug 또는 search로). 없으면 0."""
    # slug 로 먼저
    for params in ({'slug': HOT_TAG_NAME}, {'search': HOT_TAG_NAME}):
        try:
            r = requests.get(_api('tags'), params=params, headers=HEADERS, timeout=10)
            items = r.json()
            if isinstance(items, list):
                for it in items:
                    if it.get('name') == HOT_TAG_NAME or it.get('slug') == HOT_TAG_NAME:
                        return int(it.get('id', 0))
        except Exception as e:
            log.warning(f"'인기' 태그 조회 실패 ({params}): {e}")
    return 0


def _unpin_post(post_id: int, hot_tag_id: int) -> tuple[bool, str]:
    """post_id 의 sticky=False + tags에서 hot_tag_id 제거."""
    try:
        r = requests.get(_api(f'posts/{post_id}'), headers=HEADERS, timeout=10)
        if r.status_code == 404:
            return False, 'not_found'
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return False, f'GET 실패: {e}'

    current_tags = data.get('tags', []) or []
    new_tags     = [t for t in current_tags if int(t) != hot_tag_id] if hot_tag_id else current_tags

    payload = {'sticky': False}
    if hot_tag_id and len(new_tags) != len(current_tags):
        payload['tags'] = new_tags

    try:
        r = requests.post(_api(f'posts/{post_id}'), json=payload, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return True, 'ok'
    except Exception as e:
        return False, f'POST 실패: {e}'


def run():
    history = _load_history()
    if not history:
        log.info('history 비어 있음')
        return

    today = date.today()
    expired = []  # [(kw, post_id, pin_expiry)]
    for kw, info in history.items():
        exp = info.get('pin_expiry')
        pid = info.get('post_id')
        if not exp or not pid:
            continue
        try:
            exp_date = datetime.strptime(exp, '%Y-%m-%d').date()
        except ValueError:
            continue
        if exp_date <= today:
            expired.append((kw, int(pid), exp))

    if not expired:
        log.info('만료 대상 없음')
        return

    log.info(f'만료 대상: {len(expired)}개')
    hot_tag_id = _find_hot_tag_id()
    if not hot_tag_id:
        log.warning("'인기' 태그 ID를 찾지 못함 — sticky 만 해제")

    cleared = 0
    errors  = []
    for kw, pid, exp in expired:
        ok, reason = _unpin_post(pid, hot_tag_id)
        if ok:
            log.info(f'  ✓ post_id={pid} 해제 ({kw!r} / 만료일 {exp})')
            history[kw].pop('post_id',    None)
            history[kw].pop('pin_expiry', None)
            cleared += 1
        elif reason == 'not_found':
            # 포스트가 이미 삭제된 경우도 history 정리
            log.info(f'  - post_id={pid} 없음, history 정리 ({kw!r})')
            history[kw].pop('post_id',    None)
            history[kw].pop('pin_expiry', None)
            cleared += 1
        else:
            log.error(f'  ✗ post_id={pid} 실패 ({kw!r}): {reason}')
            errors.append(f'{pid} ({reason})')

    _save_history(history)

    msg_lines = [f'🧹 *[스펙분석소] 인기 고정 해제* — {cleared}/{len(expired)}건']
    if errors:
        msg_lines.append('⚠️ 실패:')
        msg_lines.extend(f'  • {e}' for e in errors[:10])
    tg.send('\n'.join(msg_lines))
    log.info(f'완료: {cleared}/{len(expired)} 해제')


if __name__ == '__main__':
    run()
