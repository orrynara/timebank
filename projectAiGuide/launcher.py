"""CanvasToon Builder Streamlit 엔트리.

요구사항:
- 인증 전에는 UI 모듈을 import하지 않는다(지연 로딩)
- 로그인 전: Thirdweb SNS/Email OTP 로그인 화면만 노출
- 로그인 후: Firestore 사용량 한도 체크 통과 시에만 탭 UI 노출
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _bootstrap_sys_path() -> None:
    """PyInstaller/Streamlit 실행 환경에서 import 경로를 안정화한다.

    - Streamlit이 실행 위치/작업 디렉터리를 바꾸는 경우에도 modules/, ui/를 찾을 수 있어야 한다.
    - PyInstaller(sys.frozen)에서는 _MEIPASS(보통 dist/.../_internal)를 루트로 보고 sys.path에 추가한다.
    """

    candidates: list[Path] = []

    here = Path(__file__).resolve()
    candidates.append(here.parent)
    candidates.append(here.parent.parent)
    candidates.append(here.parent.parent.parent)

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        base = Path(str(meipass))
        candidates.append(base)
        candidates.append(base / "app")
        candidates.append(base / "modules")

    for p in candidates:
        try:
            if p and p.exists():
                s = str(p)
                if s not in sys.path:
                    sys.path.insert(0, s)
        except Exception:
            continue


_bootstrap_sys_path()

import streamlit as st

from modules.config_loader import load_env


def _render_topbar(is_authed: bool) -> None:
    """상단 공통 영역(인증 상태/로그아웃)."""

    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎬 캔버스툰 빌더")
        if is_authed:
            user_email = str(st.session_state.get("user_email") or "").strip()
            user_id = str(st.session_state.get("user_id") or "").strip()
            display = user_email or user_id
            if display:
                st.caption(f"로그인: {display}")
    with col2:
        if is_authed:
            from modules.auth_manager import logout

            if st.button("로그아웃", width="stretch"):
                logout()
                st.rerun()


def _get_query_param(name: str) -> str:
    """Streamlit 버전 차이를 고려한 query param getter."""
    try:
        # Streamlit >= 1.30
        v = st.query_params.get(name)
        if isinstance(v, list):
            return str(v[0]) if v else ""
        return str(v or "")
    except Exception:
        try:
            qp = st.experimental_get_query_params()  # type: ignore[attr-defined]
            v = qp.get(name, [""])
            return str(v[0]) if isinstance(v, list) and v else str(v or "")
        except Exception:
            return ""


def _is_admin_user(user_id: str) -> bool:
    uid = str(user_id or "").strip()
    if not uid:
        return False

    # Super admin hard-pass
    try:
        from modules.access_control import is_superadmin

        if is_superadmin(uid):
            return True
    except Exception:
        pass

    raw = os.getenv("ADMIN_USER_IDS", "").strip()
    if not raw:
        try:
            raw = str(st.secrets.get("ADMIN_USER_IDS", ""))  # type: ignore[call-arg]
        except Exception:
            raw = ""

    allow = {x.strip() for x in raw.split(",") if x.strip()}
    return uid in allow


def main() -> None:
    """Streamlit 메인."""

    # v0.9 안정화: .env를 가능한 빨리 로드해 os.getenv 기반 설정이 누락되지 않도록 한다.
    try:
        load_env(prefer_internal=True, override=False)
    except Exception:
        pass

    st.set_page_config(page_title="캔버스툰 빌더", page_icon="🎬", layout="wide")

    # 인증 모듈만 먼저 로드(지연 로딩 핵심)
    from modules.auth_manager import is_authenticated, render_login

    authed = is_authenticated()
    _render_topbar(authed)

    if not authed:
        render_login()
        return

    user_id = str(st.session_state.get("user_id") or "").strip()
    user_email = str(st.session_state.get("user_email") or "").strip()

    # superadmin 판정(가능한 빨리)
    try:
        from modules.access_control import is_superadmin

        superadmin = bool(is_superadmin(user_email or user_id))
    except Exception:
        superadmin = False

    # auth_manager 워크플로우 정규화: user_email이 있으면 user_id에도 보강
    if user_email and not user_id:
        st.session_state["user_id"] = user_email
        user_id = user_email
    if not user_id:
        st.session_state.pop("user_id", None)
        render_login()
        return

    page = _get_query_param("page").strip().lower()
    is_admin_page = page == "admin"

    # 사용자 접근 권한 (superadmin은 항상 우회)
    from modules.access_control import is_user_allowed

    if not superadmin and not is_user_allowed(user_id) and not (is_admin_page and _is_admin_user(user_id)):
        st.error("서비스 접근 권한이 비활성화되어 있습니다. 관리자에게 문의하세요.")
        st.stop()

    # v1.03 긴급 패치: 한도 체크를 강제로 우회한다.
    # 기존 로직
    # from modules.firebase_manager import check_limit
    # limit_exceeded = bool(check_limit(user_id))
    # is_admin_user = bool(_is_admin_user(user_id)) if is_admin_page else False
    # if limit_exceeded and not superadmin and not (is_admin_page and is_admin_user):
    #     ...
    limit_exceeded = False

    # 히든 Admin 페이지 (사이드바/탭 미노출)
    if is_admin_page:
        # 수퍼어드민은 어떤 제약도 없이 즉시 접근
        if not superadmin and not _is_admin_user(user_id):
            st.error("Admin 접근 권한이 없습니다.")
            st.stop()
        from ui.page_admin import render_admin_page

        render_admin_page()
        return

    # 로그인/한도 체크 통과 이후에만 UI 모듈을 import
    from ui.tab_character import render_tab_character
    from ui.tab_dashboard import render_tab_dashboard
    from ui.tab_project import render_sidebar, render_tab_project
    from ui.tab_scenario import render_tab_scenario
    from ui.tab_system import render_tab_system

    # 좌측 메뉴(사이드바)는 탭과 무관하게 항상 렌더링
    render_sidebar()

    tab_project, tab_character, tab_scenario, tab_dashboard, tab_system = st.tabs(
        ["📁 프로젝트", "🧙 캐릭터", "🧩 시나리오", "📊 대시보드", "⚙️ 시스템"]
    )

    with tab_project:
        render_tab_project()
    with tab_character:
        render_tab_character()
    with tab_scenario:
        render_tab_scenario()
    with tab_dashboard:
        render_tab_dashboard()
    with tab_system:
        render_tab_system()


if __name__ == "__main__":
    main()
