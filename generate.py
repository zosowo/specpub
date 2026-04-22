"""
큐 생성 스크립트 — 하루 50개 분량을 생성해 queue/ 폴더에 저장.
사용: python3 generate.py [--date YYYY-MM-DD] [--count N]

스펙 글 : 기술 글 = 10 : 40 (기본값)
스펙 글이 소진되면 비율 자동 조정.
"""
import argparse
import logging
import random
from datetime import datetime, date

import catalog
import content_generator as cg
import queue_manager as qm

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

SPEC_PER_DAY  = 5
TECH_PER_DAY  = 10
TOTAL_PER_DAY = SPEC_PER_DAY + TECH_PER_DAY


def pick_spec_products(n: int) -> list:
    """발행 안 된 제품 중 n개 랜덤 선택."""
    available = [p for p in catalog.PRODUCTS if not qm.is_published(p['slug'])]
    random.shuffle(available)
    return available[:n]


def pick_tech_topics(n: int) -> list:
    """발행 안 된 기술 주제 중 n개 랜덤 선택."""
    available = [t for t in catalog.TECH_TOPICS if not qm.is_published(t['slug'])]
    random.shuffle(available)
    return available[:n]


def run(date_str: str, total: int = TOTAL_PER_DAY):
    spec_count = min(SPEC_PER_DAY, total)
    tech_count = total - spec_count

    spec_products = pick_spec_products(spec_count)
    tech_topics   = pick_tech_topics(tech_count)

    if len(spec_products) < spec_count:
        log.warning(f'스펙 제품 부족: 요청 {spec_count}개 → 가용 {len(spec_products)}개')
        tech_count += spec_count - len(spec_products)
        tech_topics = pick_tech_topics(tech_count)

    if len(tech_topics) < tech_count:
        log.warning(f'기술 주제 부족: 요청 {tech_count}개 → 가용 {len(tech_topics)}개')

    queue_items = []

    # 스펙 글 생성
    for product in spec_products:
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
            queue_items.append({
                'type':         'spec',
                'slug':         product['slug'],
                'title':        product['model'],
                'content_html': html,
                'product':      product,
            })
            log.info(f'  ✓ 생성 완료')
        except Exception as e:
            log.error(f'  오류: {e}')

    # 기술 글 생성
    for topic in tech_topics:
        log.info(f'[기술] 생성 중: {topic["title"]}')
        try:
            html = cg.generate_tech_post(topic)
            ok, reason = cg.verify_tech_content(html)
            if not ok:
                log.warning(f'  검증 실패: {reason} — 재시도')
                html = cg.generate_tech_post(topic)
                ok, reason = cg.verify_tech_content(html)
            if not ok:
                log.error(f'  재시도 후에도 실패: {reason} — 건너뜀')
                continue
            queue_items.append({
                'type':         'tech',
                'slug':         topic['slug'],
                'title':        topic['title'],
                'content_html': html,
                'product':      None,
            })
            log.info(f'  ✓ 생성 완료')
        except Exception as e:
            log.error(f'  오류: {e}')

    # 섞어서 큐에 저장
    random.shuffle(queue_items)
    for i, item in enumerate(queue_items):
        qm.save_to_queue(item, date_str, i + 1)

    log.info(f'큐 저장 완료: {len(queue_items)}개 → queue/{date_str}/')
    return len(queue_items)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date',  default=date.today().isoformat(), help='YYYY-MM-DD')
    parser.add_argument('--count', type=int, default=TOTAL_PER_DAY)
    args = parser.parse_args()

    n = run(args.date, args.count)
    print(f'완료: {n}개 생성됨')
