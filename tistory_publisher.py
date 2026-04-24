"""
티스토리 발행 — Playwright headless + 쿠키 세션.

사용 흐름:
  1. tistory_auth.py 로 tistory_storage.json 생성 (1회, 쿠키 만료 시 재실행).
  2. publish_post(title, html_body, tags, visibility) 호출.

지원 visibility:
  - "public"  : 공개 발행 (기본)
  - "private" : 비공개 저장 (본인만 볼 수 있음)
  - "draft"   : 임시저장

에디터 구조 (2026-04-24 기준, DOM inspect 로 확인):
  - 제목:      textarea#post-title-inp
  - 본문:      TinyMCE (editor-tistory, iframe #editor-tistory_ifr)
  - 태그:      input#tagText (Enter 로 확정)
  - 카테고리:  button#category-btn → 드롭다운
  - 완료:      button#publish-layer-btn → 모달
  - 모달 공개: label 안 '공개' 텍스트 span.checkbox-text
  - 모달 발행: button#publish-btn

이미지: html_body 안에 <img src="..."> hotlink 허용 (Pixabay CDN 등).
"""
from __future__ import annotations

import logging
import os
import re
import time
from typing import Optional

log = logging.getLogger(__name__)

BASE = os.path.dirname(__file__)
STORAGE_FILE = os.path.join(BASE, 'tistory_storage.json')

BLOG_URL  = os.getenv('TISTORY_BLOG_URL', 'https://dwang.tistory.com')
WRITE_URL = f'{BLOG_URL.rstrip("/")}/manage/newpost/'

_UA = (
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
)


def _set_tinymce_content(page, html_body: str) -> None:
    """TinyMCE 본문에 HTML 세팅 후 textarea 로 sync 강제.

    setContent 만으로는 iframe 내부 표시만 갱신되고 제출 시 데이터가 비어있음.
    save() 가 textarea(#editor-tistory)로 직렬화하여 폼 제출에 반영시킨다.
    """
    page.evaluate(
        """(html) => {
          if (typeof tinymce === 'undefined') {
            throw new Error('tinymce 미로드');
          }
          const ed = tinymce.get('editor-tistory');
          if (!ed) {
            throw new Error('editor-tistory 인스턴스 없음');
          }
          ed.setContent(html);
          ed.fire('change');
          ed.fire('input');
          ed.save();
          // textarea 에 input 이벤트도 디스패치 (React 상태 반영)
          const ta = document.getElementById('editor-tistory');
          if (ta) {
            const evt = new Event('input', {bubbles: true});
            ta.dispatchEvent(evt);
          }
        }""",
        html_body,
    )


def _enter_tags(page, tags: list[str]) -> None:
    """태그 input 에 엔터로 하나씩 추가."""
    if not tags:
        return
    # tagText 로딩 대기 (편집 페이지에서 늦게 렌더될 수 있음)
    try:
        page.wait_for_selector('#tagText', timeout=15000)
    except Exception:
        log.warning('[tistory] #tagText 못찾음 — 태그 입력 skip')
        return
    # 포커스
    page.click('#tagText')
    for t in tags:
        t = t.strip()
        if not t:
            continue
        # 공백 포함 태그는 티스토리가 자동으로 처리
        page.fill('#tagText', t)
        page.keyboard.press('Enter')
        page.wait_for_timeout(120)


def _click_visibility_radio(page, label_text: str) -> None:
    """모달에서 공개/비공개/공개(보호) 라디오 선택. label_text 는 '공개'/'비공개' 등."""
    # span.checkbox-text 중 text 일치하는 것 클릭 → 해당 label 체크
    ok = page.evaluate(
        """(txt) => {
          const spans = Array.from(document.querySelectorAll('label .checkbox-text'));
          const target = spans.find(s => s.textContent.trim() === txt);
          if (!target) return false;
          const lbl = target.closest('label');
          if (!lbl) return false;
          lbl.click();
          return true;
        }""",
        label_text,
    )
    if not ok:
        raise RuntimeError(f'모달 라디오 "{label_text}" 찾기 실패')


def publish_post(
    title: str,
    html_body: str,
    tags: Optional[list[str]] = None,
    visibility: str = 'public',
    category_name: Optional[str] = None,
    post_id: Optional[int] = None,
    timeout_sec: int = 75,
) -> str:
    """
    티스토리 발행 (신규) 또는 업데이트 (기존).

    post_id 가 주어지면 해당 글을 편집 — URL=/manage/newpost/<id> 로 진입.
    반환: 발행된 글 URL (공개/비공개: 실제 글 URL / 임시저장: 관리 URL).
    실패 시 RuntimeError 전파.
    """
    if visibility not in ('public', 'private', 'draft'):
        raise ValueError(f'unknown visibility: {visibility}')
    if not os.path.exists(STORAGE_FILE):
        raise RuntimeError(f'세션 파일 없음: {STORAGE_FILE} — tistory_auth.py 먼저 실행')

    from playwright.sync_api import sync_playwright

    tags = tags or []
    t0 = time.time()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            ctx = browser.new_context(storage_state=STORAGE_FILE, user_agent=_UA)
            page = ctx.new_page()
            page.set_default_timeout(timeout_sec * 1000)
            target = f'{WRITE_URL}{post_id}' if post_id else WRITE_URL
            page.goto(target, wait_until='domcontentloaded')

            page.wait_for_timeout(1500)
            # 임시저장 복원 팝업이 뜨면 '새로 작성' — 신규 작성시에만 (편집시엔 스킵)
            if post_id is None:
                try:
                    page.evaluate(
                        """() => {
                          const btns = Array.from(document.querySelectorAll('button, a'));
                          const newOne = btns.find(b => /새로 작성|새글/.test((b.textContent||'').trim()));
                          if (newOne) newOne.click();
                        }"""
                    )
                except Exception:
                    pass
                page.wait_for_timeout(500)

            # 에디터 로딩 대기
            page.wait_for_selector('#post-title-inp', timeout=15000)
            page.wait_for_function(
                "() => typeof tinymce !== 'undefined' && tinymce.get('editor-tistory')",
                timeout=20000,
            )

            # 제목
            page.fill('#post-title-inp', title)

            # 본문 (TinyMCE API 직접)
            _set_tinymce_content(page, html_body)
            page.wait_for_timeout(400)

            # 태그
            _enter_tags(page, tags)

            # 카테고리 선택 (옵션) — TinyMCE 메뉴 아이템의 텍스트 정확 일치로 매칭
            if category_name:
                try:
                    page.click('#category-btn', force=True)
                    page.wait_for_timeout(900)
                    ok = page.evaluate(
                        """(name) => {
                          // TinyMCE 메뉴 아이템이 펼쳐진 floatpanel 안에서 정확 텍스트 매칭
                          const panels = Array.from(document.querySelectorAll('.mce-floatpanel.mce-menu'));
                          for (const panel of panels) {
                            const items = Array.from(panel.querySelectorAll('.mce-menu-item, [role=menuitem], span, div'));
                            const hit = items.find(e => e.textContent.trim() === name);
                            if (hit) { hit.click(); return true; }
                          }
                          return false;
                        }""",
                        category_name,
                    )
                    if not ok:
                        log.warning(f'[tistory] 카테고리 "{category_name}" 못찾음 — 기본으로 진행')
                    else:
                        page.wait_for_timeout(400)
                except Exception as e:
                    log.warning(f'[tistory] 카테고리 설정 실패: {e}')

            # 저장/발행 분기
            if visibility == 'draft':
                # 임시저장 클릭 (span.btn-draft)
                clicked = page.evaluate(
                    """() => {
                      const el = Array.from(document.querySelectorAll('.btn-draft, span, button'))
                        .find(e => (e.textContent||'').trim().startsWith('임시저장'));
                      if (el) { el.click(); return true; }
                      return false;
                    }"""
                )
                if not clicked:
                    raise RuntimeError('임시저장 버튼 찾기 실패')
                page.wait_for_timeout(2500)
                return f'{BLOG_URL.rstrip("/")}/manage/posts'

            # 발행 직전 본문 한번 더 sync (모달 오픈시 form snapshot 보장)
            try:
                page.evaluate(
                    """() => {
                      if (typeof tinymce !== 'undefined') {
                        const ed = tinymce.get('editor-tistory');
                        if (ed) ed.save();
                      }
                    }"""
                )
            except Exception:
                pass

            # 공개/비공개: '완료' 클릭 → 모달 → 라디오 → publish-btn
            page.click('#publish-layer-btn')
            page.wait_for_selector('.ReactModal__Content', timeout=10000)
            page.wait_for_timeout(600)

            label = '공개' if visibility == 'public' else '비공개'
            _click_visibility_radio(page, label)
            page.wait_for_timeout(400)

            # 최종 발행 버튼
            # public → '공개 발행', private → '비공개 저장'
            page.click('#publish-btn')

            # 발행 후 URL 변경 대기
            try:
                page.wait_for_url(
                    re.compile(r'/entry/|/manage/'),
                    timeout=20000,
                )
            except Exception:
                pass
            page.wait_for_timeout(1500)

            final_url = page.url
            # /manage/statistics/entry/<id> 로 리다이렉트되는 경우 → 공개 URL 로 변환
            m = re.search(r'/manage/statistics/entry/(\d+)', final_url)
            if m:
                post_id = m.group(1)
                final_url = f'{BLOG_URL.rstrip("/")}/{post_id}'

            # 대개 발행 후 /entry/<slug> 로 이동하지만,
            # 관리 대시보드로 튕기는 경우도 있으므로 그 때는 recent posts 에서 추출
            if '/entry/' not in final_url and not re.search(r'/\d+/?$', final_url):
                # 최근 글 조회
                try:
                    page.goto(f'{BLOG_URL.rstrip("/")}/manage/posts', wait_until='domcontentloaded')
                    page.wait_for_timeout(1500)
                    href = page.evaluate(
                        """() => {
                          const a = document.querySelector('a[href*="/entry/"]');
                          return a ? a.href : '';
                        }"""
                    )
                    if href:
                        final_url = href
                except Exception:
                    pass

            elapsed = time.time() - t0
            log.info(f'[tistory] 발행 완료 ({elapsed:.1f}s) {visibility} → {final_url}')
            return final_url
        finally:
            browser.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    # 단독 실행 시: 임시저장으로 작동 확인
    url = publish_post(
        title='테스트 — 티스토리 자동 발행 모듈 확인',
        html_body='<p>이 글은 자동 발행 모듈 테스트용 임시저장입니다.</p>'
                  '<h2>소제목</h2><p>본문은 HTML 그대로 들어갑니다.</p>',
        tags=['테스트', '자동화'],
        visibility='draft',
    )
    print('결과:', url)
