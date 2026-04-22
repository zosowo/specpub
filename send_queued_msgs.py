"""
크론탭: 0 7 * * * — 매일 07:00 야간 작업 요약 + 큐잉된 알림 일괄 전송.

요약 내용:
  - 큐 생성 결과 (generate.py)
  - 뉴스 스캔 결과 (news_product_scanner.py)
  - 남은 카탈로그 재고 (제품/주제)
  - 23:30~06:59 사이 큐잉된 경고/에러 (있으면)
"""
import json
import logging
import os
from datetime import datetime

import catalog
import queue_manager as qm
from telegram_utils import PENDING_F, STATS_F, _do_send

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)


def _load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log.warning(f'{path} 로드 실패: {e}')
        return None


def _remaining_stock():
    published = qm.load_published()
    queued    = qm.get_queued_slugs()
    excluded  = published | queued
    prods  = len([p for p in catalog.PRODUCTS    if p['slug'] not in excluded])
    topics = len([t for t in catalog.TECH_TOPICS if t['slug'] not in excluded])
    return prods, topics


def build_summary() -> str:
    today_label = datetime.now().strftime('%m/%d')
    stats   = _load_json(STATS_F)  or {}
    pending = _load_json(PENDING_F) or []

    lines = [f'🌅 *[스펙분석소] 야간 작업 요약* ({today_label})', '']

    gen = stats.get('generate')
    if gen:
        lines.append(f'• 큐 생성: {gen["total"]}개 (스펙 {gen["specs"]} + 기술 {gen["topics"]})')
    else:
        lines.append('• 큐 생성: ⚠️ 실행 기록 없음')

    ns = stats.get('news_scan')
    if ns:
        lines.append(
            f'• 뉴스 스캔: {ns["articles"]}건 → 후보 {ns["candidates"]}건 '
            f'(추가 {ns["added"]} / 대기 {ns["upcoming"]})'
        )
    else:
        lines.append('• 뉴스 스캔: ⚠️ 실행 기록 없음')

    prods, topics = _remaining_stock()
    spec_days = prods  // 5  if prods  else 0
    tech_days = topics // 10 if topics else 0
    lines.append(f'• 남은 재고: 제품 {prods}개 (~{spec_days}일) / 주제 {topics}개 (~{tech_days}일)')

    if pending:
        lines.append('')
        lines.append(f'⚠️ *야간 알림 ({len(pending)}건):*')
        for m in pending:
            lines.append('')
            lines.append(m['text'])

    return '\n'.join(lines)


def run():
    msg = build_summary()
    _do_send(msg)
    log.info('야간 요약 전송 완료')

    for f in (PENDING_F, STATS_F):
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception as e:
                log.warning(f'{f} 삭제 실패: {e}')


if __name__ == '__main__':
    run()
