"""
크론 발행 스크립트 — 큐에서 1개 꺼내 WordPress에 발행 후 텔레그램 알림.
크론탭: 0 8-22 * * * /usr/bin/python3 /home/zosowo/specpub/publish_next.py >> /home/zosowo/specpub/publish.log 2>&1
"""
import os
import sys
import logging
from dotenv import load_dotenv

import queue_manager as qm
import telegram_utils as tg
import wp_publisher as wp

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)



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
        elif item['type'] == 'trend':
            is_hot = bool(item.get('is_hot'))
            url, post_id = wp.publish_trend_post(title, slug, html, is_hot=is_hot)

            # 인기 태그 붙은 경우 만료일을 keyword_history 에 기록
            if is_hot and post_id:
                try:
                    import json
                    from datetime import datetime, timedelta
                    from trend_generator import KW_HIST_F, PIN_DAYS
                    if os.path.exists(KW_HIST_F):
                        with open(KW_HIST_F, encoding='utf-8') as f:
                            hist = json.load(f)
                        expiry = (datetime.now() + timedelta(days=PIN_DAYS)).date().isoformat()
                        for kw in item.get('keywords', []):
                            if kw in hist:
                                hist[kw]['post_id']    = post_id
                                hist[kw]['pin_expiry'] = expiry
                        tmp = KW_HIST_F + '.tmp'
                        with open(tmp, 'w', encoding='utf-8') as f:
                            json.dump(hist, f, ensure_ascii=False, indent=2)
                        os.replace(tmp, KW_HIST_F)
                except Exception as e:
                    log.warning(f'pin_expiry 기록 실패: {e}')

            hot_suffix = ' (인기·고정)' if is_hot else ''
            score_line = f"\n*점수:* {item.get('score', 0)}" if 'score' in item else ''
            msg = (
                f"🔥 *[스펙분석소] 트렌드 발행 완료{hot_suffix}*\n\n"
                f"*제목:* {_escape(title)}"
                f"{score_line}\n"
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
        tg.send(msg)
        log.info(f'발행 완료: {title} → {url}')

    except Exception as e:
        log.error(f'발행 실패: {title} — {e}')
        tg.send(f'⚠️ *[스펙분석소] 발행 실패*\n{_escape(title)}\n`{e}`')


if __name__ == '__main__':
    run()
