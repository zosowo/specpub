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


def load_next_queue_item() -> tuple[str, dict] | tuple[None, None]:
    """
    가장 오래된 날짜 큐에서 첫 번째 미처리 파일을 반환.
    반환: (파일경로, 아이템 dict) 또는 (None, None)
    """
    pattern = os.path.join(QUEUE_DIR, '*', '*.json')
    files = sorted(glob.glob(pattern))
    for path in files:
        with open(path, encoding='utf-8') as f:
            item = json.load(f)
        if not is_published(item['slug']):
            return path, item
    return None, None


def delete_queue_file(path: str):
    try:
        os.remove(path)
    except OSError:
        pass


def queue_count() -> int:
    return len(glob.glob(os.path.join(QUEUE_DIR, '*', '*.json')))


def published_count() -> int:
    return len(load_published())
