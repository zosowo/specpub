"""
티스토리 세션 관리.

사용 흐름:
  1. 사용자가 Chrome Cookie Editor 등으로 tistory.com 쿠키 JSON 내보냄.
  2. python3 tistory_auth.py [cookies.json]  또는  기본 tistory_cookies.json.
     → Playwright 호환 storage_state 로 변환 (tistory_storage.json).
  3. 발행 모듈이 storage_state 로 컨텍스트 생성.

필수 쿠키: TSSESSION + _T_ANO (티스토리 로그인 세션).
"""
import json
import logging
import os
import sys

log = logging.getLogger(__name__)

BASE = os.path.dirname(__file__)
COOKIE_FILE  = os.path.join(BASE, 'tistory_cookies.json')
STORAGE_FILE = os.path.join(BASE, 'tistory_storage.json')

REQUIRED = {'TSSESSION', '_T_ANO'}

# Cookie Editor → Playwright sameSite 매핑
_SAME_SITE_MAP = {
    'no_restriction': 'None',
    'unspecified':    'Lax',
    'lax':            'Lax',
    'strict':         'Strict',
    'none':           'None',
}


def _to_playwright_cookie(c: dict) -> dict:
    """Cookie Editor 쿠키 → Playwright storage_state 쿠키."""
    same_site = _SAME_SITE_MAP.get(
        str(c.get('sameSite', 'lax')).lower(), 'Lax'
    )
    out = {
        'name':     c['name'],
        'value':    c['value'],
        'domain':   c['domain'],
        'path':     c.get('path', '/'),
        'httpOnly': bool(c.get('httpOnly', False)),
        'secure':   bool(c.get('secure', False)),
        'sameSite': same_site,
    }
    # session 쿠키가 아니면 expires 세팅
    if not c.get('session', False):
        exp = c.get('expirationDate')
        if exp:
            out['expires'] = float(exp)
    else:
        out['expires'] = -1
    return out


def load_cookies(path: str = COOKIE_FILE) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def validate(cookies: list[dict]) -> tuple[bool, set[str]]:
    names = {c['name'] for c in cookies}
    missing = REQUIRED - names
    return (not missing), missing


def build_storage_state(cookies: list[dict]) -> dict:
    return {
        'cookies': [_to_playwright_cookie(c) for c in cookies],
        'origins': [],
    }


def save_storage_state(state: dict, path: str = STORAGE_FILE) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.chmod(path, 0o600)


def main():
    src = sys.argv[1] if len(sys.argv) >= 2 else COOKIE_FILE
    if not os.path.exists(src):
        print(f'쿠키 파일 없음: {src}', file=sys.stderr)
        sys.exit(1)

    cookies = load_cookies(src)
    ok, missing = validate(cookies)
    if not ok:
        print(f'⚠️  필수 쿠키 누락: {missing}', file=sys.stderr)
        print('Chrome Cookie Editor 에서 tistory.com 로그인 상태로 다시 내보내세요.',
              file=sys.stderr)
        sys.exit(2)

    state = build_storage_state(cookies)
    save_storage_state(state)
    print(f'저장 완료: {STORAGE_FILE} (쿠키 {len(cookies)}개)')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    main()
