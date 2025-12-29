"""TimeBank Platform Launcher.

이 파일은 프로젝트의 진입점(Entry Point)입니다.
- PyInstaller 배포 환경과 로컬 개발 환경의 경로 차이를 보정합니다.
- .env 설정을 로드합니다.
- Streamlit UI를 실행합니다.
"""

import os
import sys
from pathlib import Path

def _bootstrap_sys_path() -> None:
    """실행 환경(Local/PyInstaller)에 따라 sys.path를 설정합니다."""
    candidates: list[Path] = []
    here = Path(__file__).resolve()
    
    # 1. 현재 파일의 상위 경로들 (Local)
    candidates.append(here.parent)
    
    # 2. PyInstaller _MEIPASS (Frozen)
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        base = Path(str(meipass))
        candidates.append(base)
        candidates.append(base / "modules")
        candidates.append(base / "ui")

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
from dotenv import load_dotenv

def main() -> None:
    """메인 실행 함수."""
    # 1. 환경변수 로드
    load_dotenv()

    # NOTE: st.set_page_config는 ui/home.py에서 호출되므로 여기서는 제거하거나,
    # 구조를 바꿔야 하는데, ui/home.py를 진입점으로 쓰는 것이 일반적임.
    # 하지만 launcher.py가 진입점이므로, 여기서 ui.home.main()을 직접 호출하지 않고
    # subprocess로 실행하거나, page_config를 여기서 하고 ui/home.py의 page_config를 제거해야 함.
    # 현재 ui/home.py가 메인 스크립트처럼 작성되었으므로,
    # 여기서는 단순히 ui.home 모듈을 import하고 그 안의 함수를 실행하는 방식이 아니라,
    # 'streamlit run launcher.py' 로 실행되었을 때를 가정하고 ui.home의 내용을 실행해야 함.
    
    # 수정: ui/home.py에 main()이 있고 page_config도 있음.
    # 따라서 launcher.py에서는 page_config를 하지 않고 바로 ui.home.main()을 호출하면
    # ui/home.py의 page_config가 첫 번째 Streamlit 명령어가 되어야 하므로 충돌 가능성 있음.
    # 가장 깔끔한 방법: launcher.py는 환경설정만 하고 ui/home.py의 코드를 실행하도록 함.
    
    # 여기서는 ui.home.py를 직접 실행하는 것과 동일한 효과를 내기 위해 import 후 main 실행
    # 단, ui.home.py의 set_page_config가 가장 먼저 실행되어야 함.
    
    try:
        from ui.home import main as ui_main
        ui_main()
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
