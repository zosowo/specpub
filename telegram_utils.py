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
STATS_F    = os.path.join(os.path.dirname(__file__), 'night_stats.json')
DEFAULT_SOURCE = os.getenv('TELEGRAM_SOURCE_PREFIX', 'Wordpress')

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


def _apply_source_prefix(msg: str, source: str | None) -> str:
    """메시지 맨 앞에 [Source] 식별자 부착. 이미 [xxx] 로 시작하면 덮어쓰지 않음."""
    tag = source if source is not None else DEFAULT_SOURCE
    if not tag:
        return msg
    stripped = msg.lstrip()
    if stripped.startswith('[') and ']' in stripped.split('\n', 1)[0]:
        return msg
    return f'[{tag}] {msg}'


def send(msg: str, source: str | None = None):
    """조용한 시간이면 큐에 저장, 아니면 즉시 전송.

    source: 식별자 ('Wordpress'/'Tistory'/'Blogger'). None 이면 DEFAULT_SOURCE 사용.
    """
    msg = _apply_source_prefix(msg, source)
    if _is_quiet():
        _queue_msg(msg)
    else:
        _do_send(msg)


def record_stats(section: str, data: dict):
    """야간 작업 통계를 night_stats.json에 기록. 07:00 send_queued_msgs가 요약 전송."""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        stats = {}
        if os.path.exists(STATS_F):
            with open(STATS_F, encoding='utf-8') as f:
                stats = json.load(f)
        if stats.get('date') != today:
            stats = {'date': today}
        stats[section] = data
        with open(STATS_F, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.warning(f'야간 stats 기록 실패: {e}')
