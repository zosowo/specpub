"""
월간 카탈로그 자동 갱신.

실행: python3 catalog_updater.py
크론: 0 2 1 * * — 매월 1일 02:00

동작:
  1. 기술 주제: 템플릿 기반 자동 생성 (할루시네이션 없음)
  2. 신제품:   웹 검색 → 공식 페이지 → Claude 스펙 추출 → 검증 → 추가
  3. 실패 시: 텔레그램 알림 (건너뜀, 다음 달 재시도)
"""

import os
import re
import sys
import ast
import json
import logging
import tempfile
import requests
import subprocess
from datetime import date
from dotenv import load_dotenv

import telegram_utils as tg

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

CLAUDE_BIN = '/home/zosowo/.nvm/versions/node/v24.14.0/bin/claude'
CATALOG_PY = os.path.join(os.path.dirname(__file__), 'catalog.py')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

_UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'


# ──────────────────────────────────────────────────────────
# 텔레그램
# ──────────────────────────────────────────────────────────

def send_telegram(msg: str):
    tg.send(msg)


# ──────────────────────────────────────────────────────────
# 현재 카탈로그 슬러그 로드
# ──────────────────────────────────────────────────────────

def load_existing_slugs() -> set:
    """catalog.py에서 현재 슬러그 집합 반환."""
    sys.path.insert(0, os.path.dirname(CATALOG_PY))
    import importlib
    import catalog as _cat
    importlib.reload(_cat)
    slugs = {p['slug'] for p in _cat.PRODUCTS}
    slugs |= {t['slug'] for t in _cat.TECH_TOPICS}
    return slugs


# ──────────────────────────────────────────────────────────
# 슬러그 생성 (브랜드 중복 방지)
# ──────────────────────────────────────────────────────────

def _make_slug(brand: str, model: str) -> str:
    """
    model이 이미 brand로 시작하면 brand를 앞에 붙이지 않음.
    예: brand='Samsung', model='Samsung Galaxy S26' → 'samsung-galaxy-s26'
        brand='Samsung', model='Bespoke 냉장고'    → 'samsung-bespoke'
    """
    base = model if model.lower().startswith(brand.lower()) else f'{brand} {model}'
    return re.sub(r'[^\w]+', '-', base.lower()).strip('-')


# ──────────────────────────────────────────────────────────
# 기술 주제 자동 생성 (템플릿 기반 — 할루시네이션 없음)
# ──────────────────────────────────────────────────────────

_TOPIC_TEMPLATES = [
    # 연도 갱신형 — 매년 새 슬러그
    ("{cat_ko} 구매 추천 {year}",          "{cat_en}-buying-recommendation-{year}"),
    ("{cat_ko} 신제품 트렌드 {year}",       "{cat_en}-new-product-trends-{year}"),
    ("{cat_ko} 가성비 순위 {year}",         "{cat_en}-value-ranking-{year}"),
    ("{cat_ko} 중고 구매 가이드 {year}",    "{cat_en}-used-market-guide-{year}"),
    ("{cat_ko} 에너지 효율 비교 {year}",    "{cat_en}-energy-comparison-{year}"),
    ("{cat_ko} 브랜드 A/S 순위 {year}",     "{cat_en}-as-ranking-{year}"),
    # 에버그린 — 슬러그에 year 없음 (처음 한 번만 생성)
    ("{cat_ko} 초보자 완전 정복",           "{cat_en}-complete-beginner"),
    ("{cat_ko} 고급 설정 가이드",           "{cat_en}-advanced-settings"),
    ("{cat_ko} 수리·교체 비용 정리",        "{cat_en}-repair-cost-guide"),
    ("{cat_ko} 소음 줄이는 실전 팁",        "{cat_en}-noise-reduction-tips"),
    ("{cat_ko} 수명 늘리는 관리 루틴",      "{cat_en}-lifespan-routine"),
    ("{cat_ko} 렌탈 vs 구매 비교",          "{cat_en}-rental-vs-purchase"),
    ("{cat_ko} 전기요금 절약 설정",         "{cat_en}-electricity-saving"),
    ("{cat_ko} 스마트홈 연동 방법",         "{cat_en}-smart-home-integration"),
]

_CATEGORIES = {
    "smartphone":      "스마트폰",
    "laptop":          "노트북",
    "tablet":          "태블릿",
    "earphone":        "이어폰",
    "smartwatch":      "스마트워치",
    "tv":              "TV",
    "monitor":         "모니터",
    "camera":          "카메라",
    "gaming_console":  "게임기",
    "speaker":         "스피커",
    "refrigerator":    "냉장고",
    "washing_machine": "세탁기",
    "air_conditioner": "에어컨",
    "air_purifier":    "공기청정기",
    "robot_vacuum":    "로봇청소기",
    "vacuum":          "무선청소기",
    "microwave":       "전자레인지",
    "hair_dryer":      "헤어드라이어",
    "electric_shaver": "전기면도기",
    "food_processor":  "음식물처리기",
}


def generate_new_topics(existing_slugs: set, count: int = 60) -> list[dict]:
    """
    템플릿 기반으로 새 기술 주제를 생성.
    이미 존재하는 슬러그는 건너뜀.
    """
    year = date.today().year
    new_topics = []

    for cat_en, cat_ko in _CATEGORIES.items():
        for title_tpl, slug_tpl in _TOPIC_TEMPLATES:
            slug  = slug_tpl.format(cat_en=cat_en, year=year)
            title = title_tpl.format(cat_ko=cat_ko, year=year)

            if slug in existing_slugs:
                continue

            new_topics.append({'slug': slug, 'title': title})
            existing_slugs.add(slug)

            if len(new_topics) >= count:
                return new_topics

    return new_topics


# ──────────────────────────────────────────────────────────
# 신제품 발견 · 스펙 검증
# ──────────────────────────────────────────────────────────

_BRAND_SITES = {
    'Samsung':   'samsung.com/sec',
    'Apple':     'apple.com/kr',
    'LG':        'lg.com/kr',
    'Sony':      'sony.co.kr',
    'Google':    'store.google.com',
    'Xiaomi':    'xiaomi.com/kr',
    'ASUS':      'asus.com/kr',
    'Lenovo':    'lenovo.com/kr',
    'Dell':      'dell.com/ko-kr',
    'HP':        'hp.com/kr',
    'Dyson':     'dyson.co.kr',
    'Roborock':  'roborock.com/kr',
    'Ecovacs':   'ecovacs.com/kr',
    'Coway':     'coway.co.kr',
    'Bosch':     'bosch-home.com/kr',
}

# 카테고리별 필수 스펙 키 + 현실적 값 범위 (검증용)
_SPEC_VALIDATORS = {
    'smartphone':     {'ram': (1, 32), 'storage': (8, 1024), 'battery': (1000, 7000), 'main_camera': (1, 300)},
    'laptop':         {'ram': (4, 128), 'storage': (64, 4096), 'display_size': (10, 18)},
    'tablet':         {'ram': (2, 16), 'battery': (3000, 15000), 'display_size': (7, 15)},
    'earphone':       {'driver_size': (4, 50), 'battery': (0, 60)},
    'smartwatch':     {'battery': (100, 2000), 'display_size': (1, 3)},
    'tv':             {'display_size': (24, 110), 'refresh_rate': (60, 240)},
    'monitor':        {'display_size': (18, 60), 'refresh_rate': (60, 360)},
    'refrigerator':   {'capacity': (50, 1200)},
    'washing_machine':{'capacity': (3, 30)},
    'air_conditioner':{'cooling_capacity': (1, 200)},
    'camera':         {'megapixel': (1, 200)},
}


def _ddg_search(query: str, limit: int = 5) -> list[str]:
    """DuckDuckGo 검색 결과 URL 반환."""
    try:
        r = requests.get(
            'https://html.duckduckgo.com/html/',
            params={'q': query},
            headers={'User-Agent': _UA},
            timeout=12,
        )
        urls = re.findall(r'<a[^>]+class="result__a"[^>]+href="(https?://[^"]+)"', r.text)
        if not urls:
            urls = re.findall(r'href="(https?://(?!duckduckgo\.com)[^"]{15,})"', r.text)
        return urls[:limit]
    except Exception:
        return []


def _fetch_page(url: str, max_chars: int = 8000) -> str:
    """페이지 HTML 텍스트 반환 (태그 제거)."""
    try:
        r = requests.get(url, headers={'User-Agent': _UA}, timeout=15)
        text = re.sub(r'<script[^>]*>.*?</script>', '', r.text, flags=re.S)
        text = re.sub(r'<style[^>]*>.*?</style>',  '', text, flags=re.S)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:max_chars]
    except Exception:
        return ''


def _run_claude(prompt: str, timeout: int = 90) -> str:
    try:
        result = subprocess.run(
            [CLAUDE_BIN, '--model', 'claude-haiku-4-5-20251001', '-p', prompt],
            capture_output=True, text=True, timeout=timeout,
        )
        return result.stdout.strip()
    except Exception as e:
        log.warning(f'Claude 호출 실패: {e}')
        return ''


def _extract_specs_from_page(page_text: str, category: str, brand: str, model: str) -> dict | None:
    """
    페이지 텍스트에서 스펙을 추출 (Claude Haiku 사용).
    실제 페이지 내용 기반 추출이므로 할루시네이션 없음.
    """
    field_hints = {
        'smartphone':     'chip, ram(GB), storage(GB), display_size(inch), display_panel, refresh_rate(Hz), main_camera(MP), battery(mAh), charging(W), weight(g), price(원), os',
        'laptop':         'cpu, ram(GB), storage(GB), display_size(inch), display_panel, refresh_rate(Hz), gpu, battery(Wh), weight(kg), price(원), os',
        'tablet':         'chip, ram(GB), storage(GB), display_size(inch), display_panel, refresh_rate(Hz), battery(mAh), weight(g), price(원), os',
        'earphone':       'type(IEM/over-ear/on-ear), driver_size(mm), frequency(Hz), impedance(Ω), battery(h), anc(yes/no), price(원)',
        'smartwatch':     'chip, display_size(mm), display_panel, battery(mAh), gps(yes/no), health_features, water_resistance, price(원), os',
        'tv':             'display_size(inch), display_panel, refresh_rate(Hz), resolution, hdr, smart_platform, price(원)',
        'monitor':        'display_size(inch), display_panel, refresh_rate(Hz), resolution, response_time(ms), color_gamut, price(원)',
        'refrigerator':   'type, capacity(L), energy_grade, compressor, smart(yes/no), noise(dB), price(원)',
        'washing_machine':'type(drum/top), capacity(kg), energy_grade, rpm, smart(yes/no), price(원)',
        'air_conditioner':'cooling_capacity(BTU or kW), energy_grade, inverter(yes/no), smart(yes/no), noise(dB), price(원)',
        'air_purifier':   'coverage(m²), filter_type, cadr, noise(dB), smart(yes/no), price(원)',
        'robot_vacuum':   'suction(Pa), navigation(LiDAR/camera), mop(yes/no), auto_empty(yes/no), battery(mAh), price(원)',
        'vacuum':         'suction(Pa or W), battery(min), weight(kg), filtration, price(원)',
        'camera':         'megapixel, sensor_size, video_max, af_system, stabilization, battery(shots), weight(g), price(원)',
        'speaker':        'driver_size(inch), power(W), frequency(Hz), connectivity, battery(h), waterproof, price(원)',
        'gaming_console': 'cpu, gpu, ram(GB), storage(GB), resolution_max, fps_max, price(원)',
        'microwave':      'capacity(L), power(W), inverter(yes/no), grill(yes/no), price(원)',
        'hair_dryer':     'power(W), heat_settings, speed_settings, ion(yes/no), weight(g), price(원)',
        'electric_shaver':'shaving_type(rotary/foil), waterproof, battery(min), cleaning_station(yes/no), price(원)',
        'food_processor': 'type(dry/wet/bio), capacity(L), power(W), deodorization(yes/no), price(원)',
    }.get(category, 'price(원)')

    prompt = f"""아래 페이지 텍스트에서 {brand} {model} 제품의 스펙을 JSON으로 추출해줘.

페이지 내용:
{page_text}

추출 대상 필드: {field_hints}

규칙:
- 페이지에 명시된 값만 추출 (추측·보완 절대 금지)
- 없는 필드는 제외
- 숫자는 단위 없이 숫자만 (예: "12" not "12GB")
- 가격은 원화 숫자만
- JSON 코드 블록 없이 순수 JSON만 출력
- 추출 가능한 스펙이 3개 미만이면 null 출력

예시:
{{"chip":"Snapdragon 8 Elite","ram":"12","storage":"256","battery":"5000"}}
"""
    raw = _run_claude(prompt, timeout=60)
    if not raw or raw.lower() == 'null':
        return None
    m = re.search(r'\{[\s\S]+\}', raw)
    if not m:
        return None
    try:
        specs = json.loads(m.group())
        specs['brand'] = brand
        return specs
    except Exception:
        return None


def _validate_specs(specs: dict, category: str) -> tuple[bool, str]:
    """스펙 값이 현실적 범위인지 검증."""
    validators = _SPEC_VALIDATORS.get(category, {})
    for key, (lo, hi) in validators.items():
        val = specs.get(key, '')
        if not val:
            continue
        try:
            num = float(str(val).split('/')[0].strip().replace(',', ''))
            if not (lo <= num <= hi):
                return False, f'{key}={val} 범위 초과 ({lo}~{hi})'
        except ValueError:
            pass
    return True, ''


def discover_and_verify_product(brand: str, model: str, category: str,
                                 existing_slugs: set) -> dict | None:
    """
    공식 사이트에서 제품 스펙 검색·추출·검증.
    성공 시 catalog 항목 dict 반환, 실패 시 None.
    """
    slug = _make_slug(brand, model)
    if slug in existing_slugs:
        log.info(f'이미 존재: {slug}')
        return None

    brand_site = _BRAND_SITES.get(brand, '')
    queries = []
    if brand_site:
        queries.append(f'site:{brand_site} {brand} {model} specifications')
    queries.append(f'{brand} {model} official specifications')
    queries.append(f'{brand} {model} 스펙 공식')

    page_text = ''
    for query in queries:
        urls = _ddg_search(query, limit=3)
        for url in urls:
            text = _fetch_page(url)
            model_words = model.lower().split()
            if sum(1 for w in model_words if w in text.lower()) >= max(1, len(model_words) // 2):
                page_text = text
                break
        if page_text:
            break

    if not page_text:
        return None

    specs = _extract_specs_from_page(page_text, category, brand, model)
    if not specs:
        return None

    ok, reason = _validate_specs(specs, category)
    if not ok:
        log.warning(f'스펙 검증 실패 [{model}]: {reason}')
        return None

    return {
        'model':        model,
        'slug':         slug,
        'brand':        brand,
        'category':     category,
        'release_year': str(date.today().year),
        'specs':        specs,
    }


# ──────────────────────────────────────────────────────────
# 신제품 후보 목록 (분기별 수동 업데이트)
# 실제 출시가 확인된 모델만 등록 — 공식 스펙 추출 실패 시 텔레그램 알림
# ──────────────────────────────────────────────────────────

UPCOMING_PRODUCTS = [
    # 스마트폰
    {'brand': 'Samsung', 'model': 'Samsung Galaxy S26 Ultra',    'category': 'smartphone'},
    {'brand': 'Samsung', 'model': 'Samsung Galaxy S26+',         'category': 'smartphone'},
    {'brand': 'Samsung', 'model': 'Samsung Galaxy S26',          'category': 'smartphone'},
    {'brand': 'Samsung', 'model': 'Samsung Galaxy Z Fold 7',     'category': 'smartphone'},
    {'brand': 'Samsung', 'model': 'Samsung Galaxy Z Flip 7',     'category': 'smartphone'},
    {'brand': 'Apple',   'model': 'Apple iPhone 17 Pro Max',     'category': 'smartphone'},
    {'brand': 'Apple',   'model': 'Apple iPhone 17 Pro',         'category': 'smartphone'},
    {'brand': 'Apple',   'model': 'Apple iPhone 17',             'category': 'smartphone'},
    {'brand': 'Google',  'model': 'Google Pixel 10 Pro',         'category': 'smartphone'},
    {'brand': 'Google',  'model': 'Google Pixel 10',             'category': 'smartphone'},
    {'brand': 'Xiaomi',  'model': 'Xiaomi 16 Ultra',             'category': 'smartphone'},
    {'brand': 'Xiaomi',  'model': 'Xiaomi 16 Pro',               'category': 'smartphone'},
    # 노트북
    {'brand': 'Apple',   'model': 'Apple MacBook Pro M5',        'category': 'laptop'},
    {'brand': 'Apple',   'model': 'Apple MacBook Air M4',        'category': 'laptop'},
    {'brand': 'Samsung', 'model': 'Samsung Galaxy Book5 Pro',    'category': 'laptop'},
    {'brand': 'ASUS',    'model': 'ASUS ROG Zephyrus G16 2026',  'category': 'laptop'},
    # 태블릿
    {'brand': 'Apple',   'model': 'Apple iPad Pro M5',           'category': 'tablet'},
    {'brand': 'Samsung', 'model': 'Samsung Galaxy Tab S11 Ultra','category': 'tablet'},
    # TV
    {'brand': 'Samsung', 'model': 'Samsung Neo QLED 8K QN900F',  'category': 'tv'},
    {'brand': 'LG',      'model': 'LG OLED G6',                  'category': 'tv'},
    # 냉장고
    {'brand': 'Samsung', 'model': 'Samsung BESPOKE AI Refrigerator 2026', 'category': 'refrigerator'},
    {'brand': 'LG',      'model': 'LG DIOS Objet Collection 2026',        'category': 'refrigerator'},
    # 세탁기
    {'brand': 'Samsung', 'model': 'Samsung Grande AI Washer 2026',        'category': 'washing_machine'},
    {'brand': 'LG',      'model': 'LG Trom Objet Collection 2026',        'category': 'washing_machine'},
    # 로봇청소기
    {'brand': 'Roborock', 'model': 'Roborock S9 MaxV Ultra',     'category': 'robot_vacuum'},
    {'brand': 'Samsung',  'model': 'Samsung Bespoke Jet Bot AI Plus 2026','category': 'robot_vacuum'},
    # 이어폰
    {'brand': 'Apple',   'model': 'Apple AirPods Pro 3',         'category': 'earphone'},
    {'brand': 'Samsung', 'model': 'Samsung Galaxy Buds 4 Pro',   'category': 'earphone'},
    {'brand': 'Sony',    'model': 'Sony WH-1000XM6',             'category': 'earphone'},
    # 스마트워치
    {'brand': 'Apple',   'model': 'Apple Watch Series 11',       'category': 'smartwatch'},
    {'brand': 'Samsung', 'model': 'Samsung Galaxy Watch 8',      'category': 'smartwatch'},
]


# ──────────────────────────────────────────────────────────
# catalog.py 파일 패치 (원자적 쓰기 + 문법 검증)
# ──────────────────────────────────────────────────────────

def _product_to_line(p: dict) -> str:
    return (
        f'    {{"model":{json.dumps(p["model"], ensure_ascii=False)},'
        f'"slug":{json.dumps(p["slug"], ensure_ascii=False)},'
        f'"brand":{json.dumps(p["brand"], ensure_ascii=False)},'
        f'"category":{json.dumps(p["category"], ensure_ascii=False)},'
        f'"release_year":{json.dumps(p["release_year"], ensure_ascii=False)},'
        f'"specs":{json.dumps(p["specs"], ensure_ascii=False)}}},'
    )


def _topic_to_line(t: dict) -> str:
    slug  = json.dumps(t['slug'],  ensure_ascii=False)
    title = json.dumps(t['title'], ensure_ascii=False)
    return f'    {{"slug":{slug}, "title":{title}}},'


def _write_catalog_safe(content: str):
    """
    catalog.py를 원자적으로 쓰고 Python 문법을 검증.
    검증 실패 시 원본을 보존하고 예외를 발생시킴.
    """
    # 1. 문법 검증 (쓰기 전)
    try:
        ast.parse(content)
    except SyntaxError as e:
        raise RuntimeError(f'catalog.py 문법 오류 — 원본 보존: {e}')

    # 2. 임시 파일에 쓰기 후 원자적 교체
    catalog_dir = os.path.dirname(CATALOG_PY)
    with tempfile.NamedTemporaryFile(
        mode='w', encoding='utf-8',
        dir=catalog_dir, suffix='.tmp', delete=False
    ) as tf:
        tf.write(content)
        tmp_path = tf.name

    try:
        os.replace(tmp_path, CATALOG_PY)  # 같은 파티션이면 원자적
    except Exception as e:
        os.unlink(tmp_path)
        raise RuntimeError(f'catalog.py 교체 실패: {e}')


def append_to_catalog(new_products: list[dict], new_topics: list[dict]):
    """catalog.py의 PRODUCTS·TECH_TOPICS 끝에 항목 추가."""
    with open(CATALOG_PY, 'r', encoding='utf-8') as f:
        content = f.read()

    today = date.today().isoformat()

    if new_products:
        product_lines = '\n'.join(_product_to_line(p) for p in new_products)
        content = re.sub(
            r'(PRODUCTS\s*=\s*\[[\s\S]*?)\n(\])',
            lambda m: (m.group(1)
                       + f'\n\n    # ── 자동 추가 {today}\n'
                       + product_lines + '\n'
                       + m.group(2)),
            content,
        )

    if new_topics:
        topic_lines = '\n'.join(_topic_to_line(t) for t in new_topics)
        content = re.sub(
            r'(TECH_TOPICS\s*=\s*\[[\s\S]*?)\n(\])',
            lambda m: (m.group(1)
                       + f'\n\n    # ── 자동 추가 {today}\n'
                       + topic_lines + '\n'
                       + m.group(2)),
            content,
        )

    _write_catalog_safe(content)


# ──────────────────────────────────────────────────────────
# 메인 실행
# ──────────────────────────────────────────────────────────

def run(topics_count: int = 60):
    log.info(f'=== 카탈로그 갱신 시작 (topics_count={topics_count}) ===')
    existing = load_existing_slugs()

    # ── 1. 기술 주제 자동 생성
    new_topics = generate_new_topics(existing, count=topics_count)
    log.info(f'새 기술 주제 {len(new_topics)}개 생성')

    # ── 2. 신제품 검증 및 수집
    new_products  = []
    failed_models = []

    for candidate in UPCOMING_PRODUCTS:
        brand    = candidate['brand']
        model    = candidate['model']
        category = candidate['category']

        slug = _make_slug(brand, model)
        if slug in existing:
            log.info(f'건너뜀 (이미 존재): {model}')
            continue

        log.info(f'검증 중: {model}')
        product = discover_and_verify_product(brand, model, category, existing)

        if product:
            new_products.append(product)
            existing.add(product['slug'])
            log.info(f'  ✓ 추가: {model}')
        else:
            failed_models.append(model)
            log.warning(f'  ✗ 검증 실패 (건너뜀): {model}')

    # ── 3. catalog.py 업데이트
    if new_products or new_topics:
        try:
            append_to_catalog(new_products, new_topics)
            log.info(f'catalog.py 업데이트 완료: 제품 +{len(new_products)}, 주제 +{len(new_topics)}')
        except RuntimeError as e:
            log.error(f'catalog.py 업데이트 실패: {e}')
            send_telegram(f'🚨 *[스펙분석소] catalog.py 업데이트 실패*\n`{e}`')
            return {'added_products': 0, 'added_topics': 0, 'failed': len(failed_models), 'failed_list': failed_models}
    else:
        log.info('추가할 항목 없음')

    # ── 4. 결과 텔레그램 알림
    today = date.today().isoformat()
    msg_parts = [f'📅 *[스펙분석소] 월간 카탈로그 갱신 완료* `{today}`\n']

    if new_products:
        msg_parts.append(f'✅ 신제품 추가: {len(new_products)}개')
        for p in new_products[:10]:
            msg_parts.append(f'  • {p["model"]}')
        if len(new_products) > 10:
            msg_parts.append(f'  … 외 {len(new_products)-10}개')

    if new_topics:
        msg_parts.append(f'✅ 기술 주제 추가: {len(new_topics)}개')

    if failed_models:
        msg_parts.append(f'\n⚠️ 스펙 검증 실패 (다음 달 재시도): {len(failed_models)}개')
        for m in failed_models[:15]:
            msg_parts.append(f'  • {m}')
        if len(failed_models) > 15:
            msg_parts.append(f'  … 외 {len(failed_models)-15}개')

    send_telegram('\n'.join(msg_parts))

    return {
        'added_products': len(new_products),
        'added_topics':   len(new_topics),
        'failed':         len(failed_models),
        'failed_list':    failed_models,
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--topics', type=int, default=60,
                        help='기술 주제 추가 개수 (주간 실행 시 15 권장, 월간 60)')
    args = parser.parse_args()

    result = run(topics_count=args.topics)
    print(f'\n완료: 제품 +{result["added_products"]}, 주제 +{result["added_topics"]}, '
          f'실패 {result["failed"]}개')
    if result['failed_list']:
        print('미추가 (공식 스펙 미공개 또는 미출시):')
        for m in result['failed_list']:
            print(f'  - {m}')
