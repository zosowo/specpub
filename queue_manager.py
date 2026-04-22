"""큐 관리 및 중복 방지."""
import os
import json
import glob
from datetime import datetime

BASE_DIR     = os.path.dirname(__file__)
QUEUE_DIR    = os.path.join(BASE_DIR, 'queue')
PUBLISHED_F  = os.path.join(BASE_DIR, 'published.json')


# ──────────────────────────────────────────────────────────
# Published 추적
# ──────────────────────────────────────────────────────────

def load_published() -> set:
    if not os.path.exists(PUBLISHED_F):
        return set()
    with open(PUBLISHED_F) as f:
        return set(json.load(f))


def mark_published(slug: str):
    published = load_published()
    published.add(slug)
    with open(PUBLISHED_F, 'w') as f:
        json.dump(sorted(published), f, ensure_ascii=False, indent=2)


def is_published(slug: str) -> bool:
    return slug in load_published()


# ──────────────────────────────────────────────────────────
# 큐 파일 관리
# ──────────────────────────────────────────────────────────

def queue_dir_for_date(date_str: str) -> str:
    """YYYY-MM-DD 형식 날짜의 큐 디렉토리 경로."""
    d = os.path.join(QUEUE_DIR, date_str)
    os.makedirs(d, exist_ok=True)
    return d


def save_to_queue(item: dict, date_str: str, index: int):
    """
    item 구조:
      { "type": "spec"|"tech", "slug": str, "title": str,
        "content_html": str, "product": dict|None }
    """
    d = queue_dir_for_date(date_str)
    path = os.path.join(d, f'{index:03d}_{item["slug"]}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(item, f, ensure_ascii=False, indent=2)


def get_queued_slugs() -> set:
    """현재 큐에 있는 모든 슬러그 집합 반환 (중복 생성 방지용)."""
    slugs = set()
    for path in glob.glob(os.path.join(QUEUE_DIR, '*', '*.json')):
        try:
            with open(path, encoding='utf-8') as f:
                item = json.load(f)
            slugs.add(item['slug'])
        except Exception:
            pass
    return slugs


def load_next_queue_item() -> tuple[str, dict] | tuple[None, None]:
    """
    가장 오래된 날짜 큐에서 첫 번째 미처리 파일을 반환.
    published.json을 한 번만 읽어 성능 개선.
    반환: (파일경로, 아이템 dict) 또는 (None, None)
    """
    pattern = os.path.join(QUEUE_DIR, '*', '*.json')
    files = sorted(glob.glob(pattern))
    published = load_published()  # 한 번만 읽기
    for path in files:
        try:
            with open(path, encoding='utf-8') as f:
                item = json.load(f)
        except Exception:
            continue
        if item['slug'] not in published:
            return path, item
    return None, None


def _cleanup_empty_queue_dirs():
    """발행 완료 후 빈 큐 디렉토리 삭제."""
    if not os.path.exists(QUEUE_DIR):
        return
    for dir_name in os.listdir(QUEUE_DIR):
        dir_path = os.path.join(QUEUE_DIR, dir_name)
        if os.path.isdir(dir_path) and not os.listdir(dir_path):
            try:
                os.rmdir(dir_path)
            except OSError:
                pass


def delete_queue_file(path: str):
    try:
        os.remove(path)
        _cleanup_empty_queue_dirs()
    except OSError:
        pass


def queue_count() -> int:
    return len(glob.glob(os.path.join(QUEUE_DIR, '*', '*.json')))


def published_count() -> int:
    return len(load_published())
