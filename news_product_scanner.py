"""
뉴스 DB에서 신제품 발표 자동 감지 → catalog.py 자동 업데이트.

크론: 0 3 * * * — 매일 03:00 (news_fetcher 수집 후)

동작:
  1. PostgreSQL AutoNewsItem에서 최근 24시간 기사 조회
  2. 전자기기 관련 기사 필터링
  3. Claude로 '신제품 발표 여부 + brand/model/category' 추출
  4. 기존 catalog에 없으면:
     - 스펙 즉시 검증 시도 → 성공: PRODUCTS에 추가
     - 실패(미출시·스펙 미공개): UPCOMING_PRODUCTS에 추가
  5. 텔레그램 일일 결과 보고
"""

import os
import re
import json
import logging
import subprocess
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

import psycopg2
import requests

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

BOT_TOKEN     = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID       = os.getenv('TELEGRAM_CHAT_ID')
DB_URL        = 'postgresql://postgres:victor123@localhost:5432/victor_jk'
CLAUDE_BIN    = '/home/zosowo/.nvm/versions/node/v24.14.0/bin/claude'
CATALOG_PY    = os.path.join(os.path.dirname(__file__), 'catalog.py')
UPDATER_PY    = os.path.join(os.path.dirname(__file__), 'catalog_updater.py')
PROCESSED_F   = os.path.join(os.path.dirname(__file__), 'processed_news.json')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# ── 감지 대상 키워드 ──────────────────────────────────────

_BRAND_KR = {
    '삼성': 'Samsung', '갤럭시': 'Samsung',
    '애플': 'Apple',   '아이폰': 'Apple', '아이패드': 'Apple', '맥북': 'Apple', '에어팟': 'Apple',
    'LG':   'LG',      'LG전자': 'LG',
    '소니': 'Sony',    '구글': 'Google', '픽셀': 'Google',
    '샤오미': 'Xiaomi', '다이슨': 'Dyson', '로보락': 'Roborock',
    '에코백스': 'Ecovacs', '코웨이': 'Coway',
    '보스': 'Bose',    '젠하이저': 'Sennheiser',
}

_CATEGORY_HINTS = {
    'smartphone':     ['스마트폰', '폴더블', '갤럭시S', '갤럭시Z', '아이폰', '픽셀', '엑스페리아'],
    'laptop':         ['노트북', '맥북', '갤럭시북', '라이젠북', '서피스'],
    'tablet':         ['태블릿', '아이패드', '갤럭시탭'],
    'earphone':       ['이어폰', '이어버드', '헤드폰', '헤드셋', 'AirPods', '에어팟', '버즈'],
    'smartwatch':     ['스마트워치', '갤럭시워치', '애플워치', '픽셀워치'],
    'tv':             ['TV', 'OLED TV', 'QLED', '네오QLED', '올레드TV'],
    'monitor':        ['모니터', 'OLED 모니터'],
    'camera':         ['카메라', '미러리스', '액션캠'],
    'refrigerator':   ['냉장고', '김치냉장고', '비스포크 냉장고'],
    'washing_machine':['세탁기', '건조기', '세탁건조기'],
    'air_conditioner':['에어컨', '시스템에어컨'],
    'air_purifier':   ['공기청정기'],
    'robot_vacuum':   ['로봇청소기', '로봇 청소기'],
    'vacuum':         ['무선청소기', '청소기'],
    'speaker':        ['스피커', '사운드바', '블루투스 스피커'],
    'gaming_console': ['게임기', '플스', 'PS5', '엑스박스', '닌텐도'],
    'microwave':      ['전자레인지', '오븐레인지'],
    'hair_dryer':     ['헤어드라이어', '드라이어'],
    'electric_shaver':['전기면도기', '면도기'],
    'food_processor': ['음식물처리기'],
}

_LAUNCH_KW = ['출시', '공식 출시', '정식 출시', '공개', '발표', '선보', '론칭', '공식화',
               '디자인 공개', '스펙 공개', '예약판매', '사전판매', '출시 예정']


def _has_product_signal(title: str, summary: str = '') -> bool:
    """제목·요약에 전자기기 브랜드 + 신제품 신호 모두 존재."""
    text = (title + ' ' + (summary or '')).lower()
    has_brand   = any(k.lower() in text for k in _BRAND_KR)
    has_product = any(k.lower() in text for k in sum(_CATEGORY_HINTS.values(), []))
    has_launch  = any(k in title + (summary or '') for k in _LAUNCH_KW)
    return has_brand and (has_product or has_launch)


# ── 처리 이력 ─────────────────────────────────────────────

def load_processed() -> set:
    if os.path.exists(PROCESSED_F):
        return set(json.load(open(PROCESSED_F)))
    return set()


def save_processed(links: set):
    # 최근 1000개만 보관
    lst = sorted(links)[-1000:]
    with open(PROCESSED_F, 'w') as f:
        json.dump(lst, f, ensure_ascii=False, indent=2)


# ── Claude 추출 ───────────────────────────────────────────

def _run_claude(prompt: str, timeout: int = 60) -> str:
    try:
        r = subprocess.run(
            [CLAUDE_BIN, '--model', 'claude-haiku-4-5-20251001', '-p', prompt],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip()
    except Exception as e:
        log.warning(f'Claude 호출 실패: {e}')
        return ''


def extract_product_from_news(title: str, summary: str) -> dict | None:
    """
    뉴스에서 신제품 정보 추출.
    반환: {"brand": "Samsung", "model": "Galaxy S26 Ultra", "category": "smartphone", "status": "announced|upcoming"}
    신제품 발표가 아니면 None 반환.
    """
    categories = ', '.join(_CATEGORY_HINTS.keys())
    prompt = f"""다음 뉴스 기사가 전자제품 신제품 발표·출시·공개에 관한 것인지 판단하고, 맞으면 제품 정보를 JSON으로 반환해.

제목: {title}
요약: {(summary or '')[:300]}

판단 기준:
- 실제 신제품 출시·공개·디자인 공개·스펙 발표면 추출
- 실적·투자·기업 합병·부품 공급 뉴스는 제외
- 루머·유출이면 status=upcoming, 공식 발표·출시면 status=announced

추출 필드:
- brand: 영문 제조사명 (Samsung/Apple/LG/Sony/Google/Xiaomi/Dyson/Roborock/Ecovacs/Coway/Bosch/Panasonic/Philips/Braun/Garmin/Bose/Sennheiser/Nothing/ASUS/Lenovo/Dell/HP/Microsoft)
- model: 정확한 모델명 (영문, 예: Samsung Galaxy Buds 4 Pro)
- category: {categories} 중 하나
- status: announced 또는 upcoming

신제품 뉴스가 아니면 null 출력.
JSON만 출력 (코드블록 없이).

예시: {{"brand":"Samsung","model":"Samsung Galaxy Buds 4 Pro","category":"earphone","status":"announced"}}
"""
    raw = _run_claude(prompt, timeout=30)
    if not raw or raw.lower() == 'null':
        return None
    m = re.search(r'\{[\s\S]+\}', raw)
    if not m:
        return None
    try:
        data = json.loads(m.group())
        # 필수 필드 체크
        if not all(k in data for k in ('brand', 'model', 'category', 'status')):
            return None
        if data['category'] not in _CATEGORY_HINTS:
            return None
        return data
    except Exception:
        return None


# ── catalog_updater.py UPCOMING_PRODUCTS 자동 추가 ────────

def add_to_upcoming(brand: str, model: str, category: str):
    """catalog_updater.py의 UPCOMING_PRODUCTS 리스트에 항목 추가."""
    with open(UPDATER_PY, 'r', encoding='utf-8') as f:
        content = f.read()

    entry = f"    {{'brand': {json.dumps(brand)}, 'model': {json.dumps(model)}, 'category': {json.dumps(category)}}},"

    # 이미 존재하면 건너뜀
    if json.dumps(model) in content:
        return False

    # UPCOMING_PRODUCTS 리스트 끝(닫는 ] 앞)에 삽입
    content = re.sub(
        r'(UPCOMING_PRODUCTS\s*=\s*\[[\s\S]*?)\n(\])',
        lambda m: m.group(1) + f'\n    # 뉴스 자동 감지\n{entry}\n' + m.group(2),
        content,
    )
    with open(UPDATER_PY, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


# ── 텔레그램 ──────────────────────────────────────────────

def send_telegram(msg: str):
    if not BOT_TOKEN or not CHAT_ID:
        return
    try:
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'Markdown'},
            timeout=10,
        )
    except Exception as e:
        log.warning(f'텔레그램 전송 실패: {e}')


# ── 메인 ─────────────────────────────────────────────────

def run():
    log.info('=== 뉴스 신제품 스캔 시작 ===')

    # 기존 catalog 슬러그 로드
    import sys
    sys.path.insert(0, os.path.dirname(CATALOG_PY))
    import importlib, catalog as _cat
    importlib.reload(_cat)
    existing_slugs = {p['slug'] for p in _cat.PRODUCTS}
    existing_slugs |= {t['slug'] for t in _cat.TECH_TOPICS}

    # UPCOMING_PRODUCTS 모델명도 중복 방지에 포함
    from catalog_updater import UPCOMING_PRODUCTS as _up
    upcoming_models = {p['model'] for p in _up}

    processed = load_processed()

    # DB에서 최근 24시간 기사 조회
    try:
        conn = psycopg2.connect(DB_URL)
        cur  = conn.cursor()
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        cur.execute(
            'SELECT title, link, summary FROM "AutoNewsItem" WHERE "publishedAt" >= %s ORDER BY "publishedAt" DESC',
            (since,)
        )
        articles = cur.fetchall()
        cur.close(); conn.close()
    except Exception as e:
        log.error(f'DB 조회 실패: {e}')
        send_telegram(f'⚠️ *[스펙분석소]* 뉴스 DB 조회 실패\n`{e}`')
        return

    log.info(f'조회된 기사: {len(articles)}건')

    # 1차 필터: 전자기기 관련 기사
    candidates = [
        (title, link, summary)
        for title, link, summary in articles
        if link not in processed and _has_product_signal(title, summary or '')
    ]
    log.info(f'전자기기 관련 후보: {len(candidates)}건')

    # Claude로 신제품 여부 판단
    from catalog_updater import discover_and_verify_product, append_to_catalog

    added_products   = []
    upcoming_added   = []
    not_product_news = 0

    for title, link, summary in candidates:
        log.info(f'분석: {title[:60]}')
        product_info = extract_product_from_news(title, summary or '')
        processed.add(link)

        if not product_info:
            not_product_news += 1
            continue

        brand    = product_info['brand']
        model    = product_info['model']
        category = product_info['category']
        status   = product_info['status']

        slug = re.sub(r'[^\w]+', '-', f'{brand} {model}'.lower()).strip('-')
        if slug in existing_slugs or model in upcoming_models:
            log.info(f'  이미 존재: {model}')
            continue

        log.info(f'  신제품 감지: {brand} {model} [{category}] ({status})')

        if status == 'announced':
            # 즉시 스펙 검증 시도
            verified = discover_and_verify_product(brand, model, category, existing_slugs.copy())
            if verified:
                append_to_catalog([verified], [])
                existing_slugs.add(verified['slug'])
                added_products.append(model)
                log.info(f'  ✓ catalog에 직접 추가: {model}')
            else:
                # 스펙 아직 없음 → UPCOMING에 추가
                if add_to_upcoming(brand, model, category):
                    upcoming_models.add(model)
                    upcoming_added.append(model)
                    log.info(f'  → UPCOMING에 추가: {model}')
        else:
            # 루머·유출 → UPCOMING에 추가
            if add_to_upcoming(brand, model, category):
                upcoming_models.add(model)
                upcoming_added.append(f'{model} (예정)')
                log.info(f'  → UPCOMING에 추가 (예정): {model}')

    save_processed(processed)

    # 결과 텔레그램 보고
    today = datetime.now().strftime('%Y-%m-%d')
    if added_products or upcoming_added:
        parts = [f'🔍 *[스펙분석소] 신제품 뉴스 감지* `{today}`\n']
        if added_products:
            parts.append(f'✅ catalog 즉시 추가: {len(added_products)}개')
            for m in added_products:
                parts.append(f'  • {m}')
        if upcoming_added:
            parts.append(f'📋 월간 검증 대기: {len(upcoming_added)}개')
            for m in upcoming_added:
                parts.append(f'  • {m}')
        send_telegram('\n'.join(parts))
    else:
        log.info(f'신제품 감지 없음 (후보 {len(candidates)}건 중 신제품 0건)')

    log.info(f'완료: 직접추가={len(added_products)}, 대기={len(upcoming_added)}, 비신제품={not_product_news}')


if __name__ == '__main__':
    run()
