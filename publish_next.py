"""
크론 발행 스크립트 — 큐에서 1개 꺼내 WordPress에 발행 후 텔레그램 알림.
크론탭: 0 7-23 * * * /usr/bin/python3 /home/zosowo/specpub/publish_next.py >> /home/zosowo/specpub/publish.log 2>&1

D2 런타임 롤오버:
  발행 실패 시 해당 큐 파일을 queue_pending/ 으로 이동하고, 다음 큐 아이템으로
  재시도 (최대 MAX_ROLLOVER 회). "시간당 1개 발행" 수량 보증.
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

MAX_ROLLOVER = 3


def _escape(text: str) -> str:
    for ch in r'_*`[':
        text = text.replace(ch, f'\\{ch}')
    return text


def _publish_one(item: dict) -> tuple[str, str]:
    """item 을 실제 발행. (url, msg) 반환. 실패 시 예외 전파."""
    slug  = item['slug']
    title = item['title']
    html  = item['content_html']
    hints = item.get('image_hints') or {}  # 기존 큐 호환

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
        url, post_id = wp.publish_trend_post(title, slug, html, is_hot=is_hot, image_hints=hints)

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
        url = wp.publish_tech_post(title, slug, html, image_hints=hints)
        msg = (
            f"💡 *[스펙분석소] 기술정보 발행 완료*\n\n"
            f"*제목:* {_escape(title)}\n"
            f"*링크:* {url}\n"
            f"*대기 중:* {qm.queue_count() - 1}개"
        )

    return url, msg


def run():
    if not os.getenv('WP_APP_PASSWORD', '').strip():
        log.error('WP_APP_PASSWORD 미설정 — .env 파일에 WordPress Application Password를 입력하세요.')
        sys.exit(1)

    rolled_over = []

    for attempt in range(1, MAX_ROLLOVER + 1):
        path, item = qm.load_next_queue_item()
        if not item:
            if rolled_over:
                log.warning(f'큐 소진 — 롤오버로 시도한 {len(rolled_over)}개 모두 실패')
                tg.send(
                    f'⚠️ *[스펙분석소] 발행 불가*\n'
                    f'큐 소진 (롤오버 {len(rolled_over)}개 모두 실패, pending 이동).\n'
                    f'실패: {", ".join(_escape(t) for t in rolled_over)}'
                )
            else:
                log.info('발행할 큐 아이템 없음')
            return

        slug  = item['slug']
        title = item['title']

        post_type = 'products' if item['type'] == 'spec' else 'posts'
        if wp.post_exists(slug, post_type):
            log.warning(f'이미 발행됨 (WP 확인): {slug}')
            qm.mark_published(slug)
            qm.delete_queue_file(path)
            continue  # 다음 아이템으로 (카운트 미발행 처리 안 함)

        try:
            url, msg = _publish_one(item)
            qm.mark_published(slug)
            qm.delete_queue_file(path)
            tg.send(msg)
            log.info(f'발행 완료: {title} → {url}')
            if rolled_over:
                log.info(f'(롤오버 {len(rolled_over)}개 후 성공)')
            return

        except Exception as e:
            log.error(f'[롤오버 {attempt}/{MAX_ROLLOVER}] 발행 실패: {title} — {e}')
            new_path = qm.move_to_pending(path)
            log.warning(f'  → pending 이동: {new_path}')
            rolled_over.append(title)
            tg.record_stats('publish_fail', {
                'title': title,
                'slug':  slug,
                'error': str(e),
            })
            # 다음 루프에서 다음 큐 아이템 시도

    # MAX_ROLLOVER 초과
    log.error(f'MAX_ROLLOVER({MAX_ROLLOVER}) 도달 — 이번 주기 발행 포기')
    tg.send(
        f'⚠️ *[스펙분석소] 발행 전면 실패*\n'
        f'{MAX_ROLLOVER}회 롤오버 모두 실패. pending 으로 이동됨.\n'
        f'실패 목록: {", ".join(_escape(t) for t in rolled_over)}'
    )


if __name__ == '__main__':
    run()
