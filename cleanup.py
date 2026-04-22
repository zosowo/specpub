"""
오래된 데이터 압축 보관.
크론탭: 0 4 * * 0 — 매주 일요일 04:00

대상:
  - queue/YYYY-MM-DD/ 중 7일 이상 된 날짜 디렉토리 → .tar.gz 압축 후 queue/archive/ 이동
  - *.log 중 30일 이상 된 것 → gzip 압축
  - processed_news.json — 항목 1000개 초과 시 최신 1000개만 유지 (이미 내부 처리)
"""
import glob
import gzip
import logging
import os
import shutil
import tarfile
from datetime import date, datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_DIR    = os.path.dirname(__file__)
QUEUE_DIR   = os.path.join(BASE_DIR, 'queue')
ARCHIVE_DIR = os.path.join(QUEUE_DIR, 'archive')
QUEUE_TTL   = 7   # 일 — 이 이상 된 큐 디렉토리 압축
LOG_TTL     = 30  # 일 — 이 이상 된 로그 파일 gzip


def _compress_old_queue_dirs():
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    cutoff = date.today() - timedelta(days=QUEUE_TTL)
    compressed = 0

    for dir_name in os.listdir(QUEUE_DIR):
        if dir_name == 'archive':
            continue
        dir_path = os.path.join(QUEUE_DIR, dir_name)
        if not os.path.isdir(dir_path):
            continue
        try:
            d = date.fromisoformat(dir_name)  # YYYY-MM-DD 형식만
        except ValueError:
            continue
        if d >= cutoff:
            continue

        archive_path = os.path.join(ARCHIVE_DIR, f'{dir_name}.tar.gz')
        try:
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(dir_path, arcname=dir_name)
            shutil.rmtree(dir_path)
            log.info(f'큐 압축: {dir_name}/ → archive/{dir_name}.tar.gz')
            compressed += 1
        except Exception as e:
            log.error(f'큐 압축 실패 {dir_name}: {e}')

    return compressed


def _compress_old_logs():
    cutoff = datetime.now() - timedelta(days=LOG_TTL)
    compressed = 0

    for log_path in glob.glob(os.path.join(BASE_DIR, '*.log')):
        mtime = datetime.fromtimestamp(os.path.getmtime(log_path))
        if mtime >= cutoff:
            continue
        gz_path = log_path + '.gz'
        try:
            with open(log_path, 'rb') as f_in, gzip.open(gz_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(log_path)
            log.info(f'로그 압축: {os.path.basename(log_path)} → .gz')
            compressed += 1
        except Exception as e:
            log.error(f'로그 압축 실패 {log_path}: {e}')

    return compressed


def run():
    log.info('=== cleanup 시작 ===')
    q = _compress_old_queue_dirs()
    l = _compress_old_logs()
    log.info(f'완료: 큐 {q}개, 로그 {l}개 압축')


if __name__ == '__main__':
    run()
