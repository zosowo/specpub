"""
티스토리 큐 소비자 — 크론에서 하루 6회 실행.

흐름:
  1. tistory_queue/*.json 중 가장 오래된 1건 선택
  2. tistory_publisher.publish_post() 호출
  3. 성공: 큐 파일 삭제 + tistory_published.json 에 기록
  4. 실패: tistory_queue_pending/ 으로 이동 (재시도 보류), 다음 후보 재시도

크론 권장: 4시간 간격 — 04,08,12,16,20,23시 (하루 6건)
"""
from __future__ import annotations

import glob
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

import telegram_utils as tg

BASE = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE, '.env'))

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

QUEUE_DIR    = os.path.join(BASE, 'tistory_queue')
PENDING_DIR  = os.path.join(BASE, 'tistory_queue_pending')
HISTORY_FILE = os.path.join(BASE, 'tistory_published.json')

MAX_ROLLOVER = 3   # 한 실행 내 재시도 최대 횟수
KST = timezone(timedelta(hours=9))

DEFAULT_CATEGORY_NAME = os.getenv('TISTORY_CATEGORY_NAME', 'Note')
BLOG_URL = os.getenv('TISTORY_BLOG_URL', 'https://dwang.tistory.com').rstrip('/')


def _normalize_url(url: str) -> str:
    """발행 URL 정규화 — 관리 페이지 경로가 나오면 공개 URL 로 변환."""
    if not url:
        return url
    m = re.search(r'/manage/(?:statistics/)?entry/(\d+)', url)
    if m:
        return f'{BLOG_URL}/{m.group(1)}'
    return url


def _oldest_queue_files(limit: int = MAX_ROLLOVER + 1) -> list[str]:
    files = glob.glob(os.path.join(QUEUE_DIR, '*.json'))
    files.sort(key=lambda p: os.path.basename(p))  # 파일명에 timestamp 포함
    return files[:limit]


def _move_to_pending(path: str) -> str:
    os.makedirs(PENDING_DIR, exist_ok=True)
    new_path = os.path.join(PENDING_DIR, os.path.basename(path))
    if os.path.exists(new_path):
        base, ext = os.path.splitext(new_path)
        i = 2
        while os.path.exists(f'{base}_{i}{ext}'):
            i += 1
        new_path = f'{base}_{i}{ext}'
    os.rename(path, new_path)
    return new_path


def _append_history(record: dict) -> None:
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append(record)
    # 최대 500개 유지
    history = history[-500:]
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def _publish_one(item: dict) -> str:
    """실제 발행. 성공 시 URL 반환. 실패 시 예외 전파."""
    import tistory_publisher as tp  # 지연 임포트 (Playwright 무거움)
    return tp.publish_post(
        title=item['title'],
        html_body=item['html_body'],
        tags=item.get('tags') or [],
        visibility='public',
        category_name=DEFAULT_CATEGORY_NAME,
    )


def _escape_md(text: str) -> str:
    for ch in r'_*`[':
        text = text.replace(ch, f'\\{ch}')
    return text


def _notify_success(item: dict, url: str, elapsed: float) -> None:
    title = _escape_md(item.get('title', '')[:80])
    kw    = _escape_md(item.get('keyword', '')[:40])
    cat   = item.get('category', '-')
    msg = (
        f'🟢 *발행 완료* ({elapsed:.1f}s)\n\n'
        f'📝 {title}\n'
        f'🔑 seed: {kw} ({cat})\n'
        f'🔗 {url}'
    )
    tg.send(msg, source='Tistory')


def _notify_failure(item: dict | None, reason: str) -> None:
    title = _escape_md((item or {}).get('title', '(제목불명)')[:80])
    reason = _escape_md(reason[:200])
    msg = (
        f'🔴 *발행 실패*\n\n'
        f'📝 {title}\n'
        f'⚠️ {reason}'
    )
    tg.send(msg, source='Tistory')


def main() -> int:
    candidates = _oldest_queue_files()
    if not candidates:
        log.info('큐 비어있음 — 발행 스킵')
        return 0

    rollovers = 0
    last_error = ''
    last_item: dict | None = None

    for path in candidates:
        if rollovers >= MAX_ROLLOVER:
            log.error(f'롤오버 {MAX_ROLLOVER}회 도달 — 중단')
            _notify_failure(last_item,
                            f'롤오버 {MAX_ROLLOVER}회 초과: {last_error}')
            return 2

        try:
            with open(path, encoding='utf-8') as f:
                item = json.load(f)
        except Exception as e:
            log.warning(f'큐 파싱 실패 → pending 이동: {path} ({e})')
            _move_to_pending(path)
            last_error = f'큐 파싱 실패: {e}'
            rollovers += 1
            continue

        last_item = item
        title = item.get('title', '')[:40]
        log.info(f'▶ 발행 시도: {title!r} (파일={os.path.basename(path)})')

        import time
        t0 = time.time()
        try:
            url = _publish_one(item)
        except Exception as e:
            log.error(f'✗ 발행 실패 → pending: {e}')
            _move_to_pending(path)
            last_error = str(e)
            rollovers += 1
            continue

        if not url:
            log.error('✗ 발행 결과 URL 빈 값 → pending')
            _move_to_pending(path)
            last_error = '발행 결과 URL 비어있음'
            rollovers += 1
            continue

        elapsed = time.time() - t0
        url = _normalize_url(url)
        log.info(f'✓ 발행 성공 ({elapsed:.1f}s): {url}')
        try:
            os.remove(path)
        except OSError:
            pass

        _append_history({
            'title':        item.get('title'),
            'url':          url,
            'tags':         item.get('tags'),
            'keyword':      item.get('keyword'),
            'category':     item.get('category'),
            'elapsed_sec':  round(elapsed, 1),
            'published_at': datetime.now(KST).isoformat(timespec='seconds'),
        })
        _notify_success(item, url, elapsed)
        return 0

    log.error('모든 후보 실패')
    _notify_failure(last_item, f'모든 후보 실패: {last_error}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
