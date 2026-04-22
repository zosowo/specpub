"""Claude CLI를 통한 콘텐츠 생성 — 스펙분석 / 기술정보."""
import subprocess
import json
import re


CLAUDE_BIN = '/home/zosowo/.nvm/versions/node/v24.14.0/bin/claude'
MODEL = 'claude-sonnet-4-6'


def _run_claude(prompt: str) -> str:
    result = subprocess.run(
        [CLAUDE_BIN, '--model', MODEL, '-p', prompt],
        capture_output=True, text=True, timeout=120,
    )
    return result.stdout.strip()


# ──────────────────────────────────────────────────────────
# 스펙 분석 글
# ──────────────────────────────────────────────────────────

def generate_spec_post(product: dict) -> str:
    """제품 스펙 데이터를 기반으로 스펙 분석 HTML 본문 생성."""
    specs_text = '\n'.join(f'  {k}: {v}' for k, v in product['specs'].items())
    prompt = f"""다음 스펙 데이터를 바탕으로 스펙 분석 블로그 포스트 본문을 한국어 HTML로 작성해줘.

제품명: {product['model']}
제조사: {product['brand']}
카테고리: {product['category']}
출시년도: {product.get('release_year', '2025')}
스펙:
{specs_text}

조건:
- 순수 HTML만 출력 (```html 마크다운 블록 없이)
- <article> 태그 없이 <h2>부터 시작
- 구성: 제품 소개 (2~3문장) → 주요 스펙 하이라이트 (<h2>) → 경쟁 제품과 차별점 (<h2>) → 이런 사람에게 추천 (<h2>)
- 팩트 기반, 스펙 수치를 구체적으로 언급
- 광고성 문구, 쿠팡 링크, 구매 버튼 절대 포함하지 말 것
- 면책 안내문 포함하지 말 것 (템플릿에서 자동 추가)
- 분량: 700~1000자 한국어
"""
    return _run_claude(prompt)


# ──────────────────────────────────────────────────────────
# 기술정보 글
# ──────────────────────────────────────────────────────────

def generate_tech_post(topic: dict) -> str:
    """기술 정보 주제로 교육 콘텐츠 HTML 본문 생성."""
    prompt = f"""다음 주제로 전자기기 기술 정보 블로그 포스트 본문을 한국어 HTML로 작성해줘.

주제: {topic['title']}

조건:
- 순수 HTML만 출력 (```html 마크다운 블록 없이)
- <h2>부터 시작 (제목 태그 없이)
- 구성: 개념 정의 (<h2>) → 원리/종류 (<h2>) → 실생활 적용/구매 가이드 (<h2>) → 정리 한 줄 요약
- 팩트 기반, 정확한 수치와 용어 사용
- 표(table)를 최소 1개 포함 (비교 항목 있을 경우)
- 광고성 문구, 구매 링크 절대 포함하지 말 것
- 면책 안내문 포함하지 말 것
- 분량: 800~1200자 한국어
"""
    return _run_claude(prompt)


# ──────────────────────────────────────────────────────────
# 검증
# ──────────────────────────────────────────────────────────

def verify_spec_content(product: dict, html: str) -> tuple[bool, str]:
    """
    생성된 스펙 글이 팩트 기반인지 기본 검증.
    반환: (통과 여부, 실패 이유)
    """
    if len(html) < 300:
        return False, f'본문이 너무 짧음 ({len(html)}자)'
    if not re.search(r'<h2', html, re.IGNORECASE):
        return False, 'H2 섹션 없음'

    # 핵심 스펙 수치가 본문에 언급되는지 확인
    key_checks = []
    for key in ('ram', 'battery', 'chip', 'cpu'):
        val = product['specs'].get(key, '')
        if val:
            key_checks.append(val.split('/')[0].strip())

    missing = [v for v in key_checks if v and v not in html]
    if len(missing) > len(key_checks) // 2:
        return False, f'핵심 스펙 수치 누락: {missing}'

    if '쿠팡' in html or '구매하기' in html or '최저가' in html:
        return False, '광고성 문구 포함'

    return True, ''


def verify_tech_content(html: str) -> tuple[bool, str]:
    if len(html) < 400:
        return False, f'본문이 너무 짧음 ({len(html)}자)'
    if not re.search(r'<h2', html, re.IGNORECASE):
        return False, 'H2 섹션 없음'
    if '쿠팡' in html or '구매하기' in html:
        return False, '광고성 문구 포함'
    return True, ''
