from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path


def _prepend_paths(var: str, paths: list[str]) -> None:
    raw = os.environ.get(var, "") or ""
    parts = [p for p in raw.split(os.pathsep) if p]
    for p in paths:
        p = str(p or "").strip()
        if not p:
            continue
        if p not in parts:
            parts.insert(0, p)
    os.environ[var] = os.pathsep.join(parts)


def _wait_for_port(host: str, port: int, timeout_sec: float) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except Exception:
            time.sleep(0.2)
    return False


def _open_browser_when_ready(url: str, *, host: str, port: int) -> None:
    try:
        if _wait_for_port(host, port, timeout_sec=60.0):
            webbrowser.open(url)
    except Exception:
        pass


def _bundled_path(*parts: str) -> Path:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(str(meipass), *parts)
    return Path(__file__).resolve().parent.joinpath(*parts)


def _load_dotenv_from(path: Path, *, override: bool) -> None:
    if not path.exists() or not path.is_file():
        return

    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export ") :].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                continue
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            if (not override) and (key in os.environ):
                continue
            os.environ[key] = value
    except Exception as e:
        print(f"[portable_entry] .env 로드 실패: {path} ({e})")


def _bundled_launcher_path() -> str:
    # 빌드 스크립트: --add-data "launcher.py;app"
    p = _bundled_path("app", "launcher.py")
    if p.exists() and p.is_file():
        return str(p)

    # dev fallback (repo root에서 실행할 때)
    here = Path(__file__).resolve().parent
    p2 = here.parent / "launcher.py"
    return str(p2)


def _parse_port(raw: str) -> int | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        port = int(raw)
    except ValueError:
        return None
    if 1 <= port <= 65535:
        return port
    return None


def _read_default_port_file() -> int | None:
    # 프로젝트별 기본 포트를 "코드"가 아니라 "설정"으로 관리하기 위한 파일.
    # - 빌드 시: scripts/build_portable_exe_onedir.ps1가 data/default_port.txt를 생성/번들
    # - 런타임: data/.env의 PORT가 없을 때 fallback
    p = _bundled_path("data", "default_port.txt")
    if not p.exists() or not p.is_file():
        return None
    try:
        return _parse_port(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _resolve_port() -> int:
    # 1) 환경변수 PORT 우선 (번들된 data/.env 로드 결과 포함)
    env_port = _parse_port(os.getenv("PORT", ""))
    if env_port is not None:
        return env_port

    # 2) 번들된 기본값 파일
    file_port = _read_default_port_file()
    if file_port is not None:
        return file_port

    # 3) 최후 fallback (설정 누락 대비)
    return 8889


def main() -> None:
    # 1) 번들된 .env를 우선 로드 (빌드 스크립트: --add-data ".env;data/.env")
    env_path = _bundled_path("data", ".env")
    _load_dotenv_from(env_path, override=False)

    # 2) Streamlit 개발 모드 비활성화(배포 안정성)
    os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
    os.environ.setdefault("STREAMLIT_CLIENT_TOOLBAR_MODE", "viewer")

    # 3) PyInstaller 환경에서 import 경로 보강
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        base = str(meipass)
        # 현재 프로세스(import) + Streamlit 내부 동적 import를 위해 둘 다 보강
        for p in [os.path.join(base, "app"), base]:
            if p and p not in sys.path:
                sys.path.insert(0, p)
        _prepend_paths("PYTHONPATH", [os.path.join(base, "app"), base])

    # 4) 브라우저 오픈 (서버가 뜬 뒤)
    # 포트 우선순위: data/.env의 PORT > data/default_port.txt > fallback
    port = _resolve_port()
    url = f"http://localhost:{port}"

    threading.Thread(
        target=_open_browser_when_ready,
        args=(url,),
        kwargs={"host": "127.0.0.1", "port": port},
        daemon=True,
    ).start()

    launcher_path = _bundled_launcher_path()

    # 5) Streamlit CLI를 프로그램적으로 호출
    # - PyInstaller 배포 환경에서 bootstrap.run의 flag 적용이 무시되는 케이스가 있어
    #   CLI 경로를 사용해 --server.port=8889를 확실히 강제한다.
    from streamlit.web import cli as stcli  # type: ignore

    sys.argv = [
        "streamlit",
        "run",
        launcher_path,
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--global.developmentMode",
        "false",
        "--client.toolbarMode",
        "viewer",
    ]

    try:
        stcli.main()
    except SystemExit as e:
        # Streamlit CLI 내부에서 sys.exit를 호출할 수 있어 프로세스가 바로 종료될 수 있다.
        # 종료를 방어적으로 막고, 로그를 남긴다.
        print(f"[portable_entry] Streamlit CLI SystemExit intercepted: code={e.code}")
        while True:
            time.sleep(3600)


if __name__ == "__main__":
    main()
