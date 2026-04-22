"""
크론 발행 스크립트 — 큐에서 1개 꺼내 WordPress에 발행 후 텔레그램 알림.
크론탭: 0 8-22 * * * /usr/bin/python3 /home/zosowo/specpub/publish_next.py >> /home/zosowo/specpub/publish.log 2>&1
"""
import os
import sys
import logging
import requests
from dotenv import load_dotenv

import queue_manager as qm
import wp_publisher as wp

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID   = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)


def send_telegram(msg: str):
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        resp = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'},
            timeout=10,
        )
        if resp.status_code != 200:
            requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                json={'chat_id': CHAT_ID, 'text': msg},
                timeout=10,
            )
    except Exception as e:
        log.warning(f'텔레그램 전송 실패: {e}')


def _escape(text: str) -> str:
    for ch in r'_*`[':
        text = text.replace(ch, f'\\{ch}')
    return text


def run():
    # Application Password 미설정 체크
    if not os.getenv('WP_APP_PASSWORD', '').strip():
        log.error('WP_APP_PASSWORD 미설정 — .env 파일에 WordPress Application Password를 입력하세요.')
        sys.exit(1)

    path, item = qm.load_next_queue_item()
    if not item:
        log.info('발행할 큐 아이템 없음')
        return

    slug  = item['slug']
    title = item['title']
    html  = item['content_html']

    # 중복 확인 (WP에도 직접 확인)
    post_type = 'products' if item['type'] == 'spec' else 'posts'
    if wp.post_exists(slug, post_type):
        log.warning(f'이미 발행됨 (WP 확인): {slug}')
        qm.mark_published(slug)
        qm.delete_queue_file(path)
        return

    try:
        if item['type'] == 'spec':
            url = wp.publish_spec_post(item['product'], html)
            category = item['product']['category']
            cat_labels = {
                'smartphone':     ('📱', '스마트폰'),
                'laptop':         ('💻', '노트북'),
                'tablet':         ('📲', '태블릿'),
                'earphone':       ('🎧', '이어폰·헤드폰'),
                'smartwatch':     ('⌚', '스마트워치'),
                'tv':             ('📺', 'TV'),
                'monitor':        ('🖥', '모니터'),
                'camera':         ('📷', '카메라'),
                'gaming_console': ('🎮', '게임기'),
                'speaker':        ('🔊', '스피커'),
                'refrigerator':   ('🧊', '냉장고'),
                'washing_machine':('🫧', '세탁기'),
                'air_conditioner':('❄️', '에어컨'),
                'air_purifier':   ('🌬️', '공기청정기'),
                'robot_vacuum':   ('🤖', '로봇청소기'),
                'vacuum':         ('🌀', '청소기'),
                'microwave':      ('📡', '전자레인지'),
                'hair_dryer':     ('💨', '헤어드라이어'),
                'electric_shaver':('🪒', '전기면도기'),
                'food_processor': ('♻️', '음식물처리기'),
            }
            emoji, cat_label = cat_labels.get(category, ('📦', category))
            msg = (
                f"{emoji} *[스펙분석소] 발행 완료*\n\n"
                f"*제목:* {_escape(title)}\n"
                f"*분류:* {cat_label}\n"
                f"*링크:* {url}\n"
                f"*대기 중:* {qm.queue_count() - 1}개"
            )
        else:
            url = wp.publish_tech_post(title, slug, html)
            msg = (
                f"💡 *[스펙분석소] 기술정보 발행 완료*\n\n"
                f"*제목:* {_escape(title)}\n"
                f"*링크:* {url}\n"
                f"*대기 중:* {qm.queue_count() - 1}개"
            )

        qm.mark_published(slug)
        qm.delete_queue_file(path)
        send_telegram(msg)
        log.info(f'발행 완료: {title} → {url}')

    except Exception as e:
        log.error(f'발행 실패: {title} — {e}')
        send_telegram(f'⚠️ *[스펙분석소] 발행 실패*\n{_escape(title)}\n`{e}`')


if __name__ == '__main__':
    run()
