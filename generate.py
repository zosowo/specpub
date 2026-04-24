"""
큐 생성 스크립트 — 하루 15개 분량을 생성해 queue/ 폴더에 저장.
사용: python3 generate.py [--date YYYY-MM-DD] [--count N]

스펙 글 : 기술 글 = 5 : 10 (기본값)
스펙 글이 소진되면 기술 글로 자동 보완.
0개 생성 시 텔레그램 알림.

이미지 Dry-Run 필터 (D1'):
  본문 생성(Claude 호출) 전에 이미지 후보 탐색만 먼저 실행.
  매칭 실패한 주제는 큐에서 제외, catalog 에는 그대로 (다음날 재시도).
  → 제네릭/엉뚱한 이미지로 발행되는 것을 원천 차단 + Claude 토큰 절감.
"""
import os
import argparse
import logging
import random
from datetime import date
from dotenv import load_dotenv

import catalog
import content_generator as cg
import queue_manager as qm
import telegram_utils as tg
import wp_publisher as wp

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

SPEC_PER_DAY  = 5
TECH_PER_DAY  = 10
TOTAL_PER_DAY = SPEC_PER_DAY + TECH_PER_DAY

# Dry-Run 필터에서 탈락률을 감안해 후보를 넉넉히 뽑는 배수
CANDIDATE_MULT = 3


def _available_spec_products() -> list:
    """미발행·미큐잉된 스펙 제품 전체 (랜덤 셔플된 순서)."""
    published = qm.load_published()
    queued    = qm.get_queued_slugs()
    excluded  = published | queued
    available = [p for p in catalog.PRODUCTS if p['slug'] not in excluded]
    random.shuffle(available)
    return available


def _available_tech_topics() -> list:
    """미발행·미큐잉된 기술 주제 전체 (랜덤 셔플된 순서)."""
    published = qm.load_published()
    queued    = qm.get_queued_slugs()
    excluded  = published | queued
    available = [t for t in catalog.TECH_TOPICS if t['slug'] not in excluded]
    random.shuffle(available)
    return available


def _build_queue_items_spec(need: int) -> tuple[list, int]:
    """스펙 글 need 개 큐 아이템 생성. 반환: (queue_items, dryrun_탈락 수)."""
    pool = _available_spec_products()
    items, dryrun_fail = [], 0

    for product in pool:
        if len(items) >= need:
            break

        if not wp.has_image_candidate_product(product):
            log.warning(f'[스펙·이미지탈락] {product["model"]} — 큐 제외')
            dryrun_fail += 1
            continue

        log.info(f'[스펙] 생성 중: {product["model"]}')
        try:
            html = cg.generate_spec_post(product)
            ok, reason = cg.verify_spec_content(product, html)
            if not ok:
                log.warning(f'  검증 실패: {reason} — 재시도')
                html = cg.generate_spec_post(product)
                ok, reason = cg.verify_spec_content(product, html)
            if not ok:
                log.error(f'  재시도 후에도 실패: {reason} — 건너뜀')
                continue
            items.append({
                'type':         'spec',
                'slug':         product['slug'],
                'title':        product['model'],
                'content_html': html,
                'product':      product,
            })
            log.info(f'  ✓ 생성 완료 ({len(items)}/{need})')
        except Exception as e:
            log.error(f'  오류: {e}')

    return items, dryrun_fail


def _build_queue_items_tech(need: int) -> tuple[list, int]:
    """기술 글 need 개 큐 아이템 생성. 반환: (queue_items, dryrun_탈락 수)."""
    pool = _available_tech_topics()
    items, dryrun_fail = [], 0

    for topic in pool:
        if len(items) >= need:
            break

        if not wp.has_image_candidate_tech(topic['title'], topic['slug']):
            log.warning(f'[기술·이미지탈락] {topic["title"]} — 큐 제외')
            dryrun_fail += 1
            continue

        log.info(f'[기술] 생성 중: {topic["title"]}')
        try:
            html, hints = cg.generate_tech_post(topic)
            ok, reason = cg.verify_tech_content(html)
            if not ok:
                log.warning(f'  검증 실패: {reason} — 재시도')
                html, hints = cg.generate_tech_post(topic)
                ok, reason = cg.verify_tech_content(html)
            if not ok:
                log.error(f'  재시도 후에도 실패: {reason} — 건너뜀')
                continue
            items.append({
                'type':         'tech',
                'slug':         topic['slug'],
                'title':        topic['title'],
                'content_html': html,
                'image_hints':  hints,
                'product':      None,
            })
            if hints.get('products') or hints.get('keywords'):
                log.info(f'  ✓ 생성 완료, hints={hints} ({len(items)}/{need})')
            else:
                log.info(f'  ✓ 생성 완료 (hints 없음, {len(items)}/{need})')
        except Exception as e:
            log.error(f'  오류: {e}')

    return items, dryrun_fail


def run(date_str: str, total: int = TOTAL_PER_DAY):
    spec_count = min(SPEC_PER_DAY, total)
    tech_count = total - spec_count

    spec_items, spec_dryfail = _build_queue_items_spec(spec_count)
    # 스펙 부족분을 기술로 보완
    if len(spec_items) < spec_count:
        shortfall = spec_count - len(spec_items)
        tech_count += shortfall
        log.warning(f'스펙 부족: 요청 {spec_count} → 생성 {len(spec_items)} (기술 {shortfall} 보완)')

    tech_items, tech_dryfail = _build_queue_items_tech(tech_count)
    if len(tech_items) < tech_count:
        log.warning(f'기술 부족: 요청 {tech_count} → 생성 {len(tech_items)}')

    queue_items = spec_items + tech_items

    random.shuffle(queue_items)
    for i, item in enumerate(queue_items):
        qm.save_to_queue(item, date_str, i + 1)

    log.info(
        f'큐 저장 완료: {len(queue_items)}개 → queue/{date_str}/ '
        f'(이미지 Dry-Run 탈락: 스펙 {spec_dryfail}, 기술 {tech_dryfail})'
    )

    specs  = len([i for i in queue_items if i['type'] == 'spec'])
    topics = len([i for i in queue_items if i['type'] == 'tech'])
    tg.record_stats('generate', {
        'specs':   specs,
        'topics':  topics,
        'total':   len(queue_items),
        'image_dryrun_fail_spec': spec_dryfail,
        'image_dryrun_fail_tech': tech_dryfail,
    })

    if len(queue_items) == 0:
        remaining_products = len([p for p in catalog.PRODUCTS if not qm.is_published(p['slug'])])
        remaining_topics   = len([t for t in catalog.TECH_TOPICS if not qm.is_published(t['slug'])])
        tg.send(
            f'⚠️ *[스펙분석소] generate.py 경고*\n'
            f'오늘 큐 생성 0개 (이미지 Dry-Run 탈락 스펙 {spec_dryfail}, 기술 {tech_dryfail})\n'
            f'남은 제품: {remaining_products}개 / 남은 기술 주제: {remaining_topics}개\n'
            f'catalog_updater.py 실행 또는 카탈로그 추가 필요'
        )

    return len(queue_items)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date',  default=date.today().isoformat(), help='YYYY-MM-DD')
    parser.add_argument('--count', type=int, default=TOTAL_PER_DAY)
    args = parser.parse_args()

    n = run(args.date, args.count)
    print(f'완료: {n}개 생성됨')
