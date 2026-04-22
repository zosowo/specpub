"""
텔레그램 알림 유틸 — 조용한 시간대(23:30~06:59) 메시지 큐잉.
23:30~06:59 사이 발생한 알림은 pending_telegram.json에 저장,
07:00 크론(send_queued_msgs.py)이 일괄 전송.
"""
import json
import logging
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

BOT_TOKEN  = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID    = os.getenv('TELEGRAM_CHAT_ID')
PENDING_F  = os.path.join(os.path.dirname(__file__), 'pending_telegram.json')

log = logging.getLogger(__name__)

# 조용한 시간대: 23:30 ~ 06:59
_QUIET_START = (23, 30)
_QUIET_END   = (7, 0)


def _is_quiet() -> bool:
    now = datetime.now()
    h, m = now.hour, now.minute
    after_start  = (h, m) >= _QUIET_START
    before_end   = (h, m) < _QUIET_END
    return after_start or before_end  # 자정 넘겨도 조용한 시간


def _do_send(msg: str):
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'},
            timeout=10,
        )
        if r.status_code != 200:
            requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                json={'chat_id': CHAT_ID, 'text': msg},
                timeout=10,
            )
    except Exception as e:
        log.warning(f'텔레그램 전송 실패: {e}')


def _queue_msg(msg: str):
    try:
        msgs = []
        if os.path.exists(PENDING_F):
            with open(PENDING_F, encoding='utf-8') as f:
                msgs = json.load(f)
        msgs.append({'time': datetime.now().isoformat(), 'text': msg})
        with open(PENDING_F, 'w', encoding='utf-8') as f:
            json.dump(msgs, f, ensure_ascii=False, indent=2)
        log.info(f'텔레그램 조용한 시간 — 큐에 저장 ({len(msgs)}건 대기)')
    except Exception as e:
        log.warning(f'텔레그램 큐 저장 실패: {e}')


def send(msg: str):
    """조용한 시간이면 큐에 저장, 아니면 즉시 전송."""
    if _is_quiet():
        _queue_msg(msg)
    else:
        _do_send(msg)
