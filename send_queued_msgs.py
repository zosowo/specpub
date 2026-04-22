"""
크론탭: 0 7 * * * — 매일 07:00, 조용한 시간 동안 쌓인 텔레그램 메시지 일괄 전송.
"""
import json
import logging
import os
from datetime import datetime

from telegram_utils import PENDING_F, _do_send

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)


def run():
    if not os.path.exists(PENDING_F):
        log.info('대기 메시지 없음')
        return

    with open(PENDING_F, encoding='utf-8') as f:
        msgs = json.load(f)

    if not msgs:
        log.info('대기 메시지 없음')
        return

    log.info(f'{len(msgs)}건 전송 시작')
    header = f'🌅 *[스펙분석소] 야간 알림 모음* ({datetime.now().strftime("%m/%d")})\n\n'
    body   = '\n\n─────\n\n'.join(m['text'] for m in msgs)
    _do_send(header + body)

    os.remove(PENDING_F)
    log.info('전송 완료, 큐 초기화')


if __name__ == '__main__':
    run()
