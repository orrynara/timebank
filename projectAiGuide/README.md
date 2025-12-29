# projectAiGuide (이식/보존용 패키지)

이 폴더는 **CanvasToon_Builder에서 검증된 개발 룰 + 배포(Portable EXE) 빌드 시스템**을 다른 프로젝트로 이식할 때 필요한 핵심 자산을 보관합니다.

> 주의: 이 폴더에는 **실제 키/민감정보를 포함하지 않습니다.** (`.env`는 포함하지 않음)

---

## 포함 파일과 역할

- `modules/AI_RULES.md`
  - AI 에이전트가 코드를 수정/생성할 때 따라야 하는 **개발 표준**입니다.
  - 특히 Streamlit re-run 환경에서 발생하기 쉬운 NameError/상태 단절을 막기 위해 **“파일 수정 시 전체 재작성(Full Rewrite)”** 원칙을 명시합니다.

- `modules/__init__.py`, `modules/project_manager.py`
  - 새 프로젝트에서도 `from modules.project_manager import ProjectManager` / `import modules.project_manager as pm` 형태가 그대로 동작하도록 **패키지 구조를 보존**한 프로젝트 관리 모듈입니다.
  - 표준 라이브러리 기반(외부 API 미의존)이라 이식성이 높습니다.

- `.env.template`
  - **실제 키가 비어있는 환경변수 템플릿**입니다.
  - 새 프로젝트에서 `.env`로 복사 후 값을 채우는 용도입니다.

- `requirements.txt`
  - 개발/실행에 필요한 Python 의존성 목록입니다.

- `launcher.py`
  - Streamlit 앱의 **진입점(Entry)** 입니다.
  - 핵심: `_bootstrap_sys_path()`로 **부트스트랩 경로 주입**을 수행해,
    - 작업 디렉터리(CWD)가 달라도 `modules/`, `ui/` import가 안정적으로 동작하고
    - PyInstaller 실행 시 `sys._MEIPASS`(번들 내부 경로)에서도 import 경로가 무너지지 않도록 합니다.
  - 또한 인증 전/후에 import를 분리하는 **지연 로딩(로그인 전 UI 모듈 미-import)** 패턴을 포함합니다.

- `portable_entry.py`
  - PyInstaller EXE에서 Streamlit 서버를 실행하기 위한 **배포용 엔트리**입니다.
  - 핵심: `_bundled_launcher_path()`로 번들 내부의 `launcher.py`를 정확히 찾아 `streamlit run`에 전달합니다.
  - 또한 PyInstaller 환경에서는 `PYTHONPATH`를 주입해 자식 프로세스(Streamlit 런타임)에서도 모듈 탐색이 되도록 보강합니다.

- `scripts/build_portable_exe_onedir.ps1`
  - Windows에서 PyInstaller로 **onedir 포터블 빌드**를 생성하는 스크립트입니다.
  - 스크립트 내부에서 `$PSScriptRoot/..`를 프로젝트 루트로 가정하므로 **`scripts/` 아래에 두는 구조를 그대로 유지**하는 것이 안전합니다.

- `.cursorrules`
  - 이 저장소에는 파일이 존재하지 않아 포함되지 않았습니다(존재 시 복사 대상).

- (정리) 루트 `project_manager.py`
  - 기존에 projectAiGuide 루트에 중복 파일이 있었으나, 현행 시스템의 import 경로(`modules.project_manager`)와 혼동을 줄이기 위해 **삭제**했습니다.

---

## 오늘 해결한 핵심 포인트 (중요)

### 1) 부트스트랩 경로 주입 (launcher.py)
Streamlit/PyInstaller 환경에서는 실행 위치가 바뀌거나 번들 내부 경로(`sys._MEIPASS`)에서 실행되면서 `import modules...`, `import ui...`가 실패하기 쉽습니다.

- `launcher.py`의 `_bootstrap_sys_path()`가 **후보 경로들을 sys.path 앞쪽에 주입**해 import를 안정화합니다.
- 이 로직이 없으면 EXE에서는 `ModuleNotFoundError`가 나거나, Streamlit re-run 시 경로가 흔들려 실행이 불안정해질 수 있습니다.

### 2) PyInstaller 의존성 수집 (ps1)
Streamlit은 동적 import가 많고, tkinter는 Tcl/Tk 런타임 데이터가 필요할 수 있어 **“빌드는 되지만 실행이 깨지는”** 케이스가 자주 발생합니다.

- `--add-data`로 런타임 필수 파일/폴더를 번들에 포함합니다.
  - 예: `launcher.py;app`, `ui`, `modules`, `assets`, `projects`, `.env;data/.env`
- `--collect-all`, `--hidden-import`로 누락되기 쉬운 패키지를 보강합니다.
- Tcl/Tk 루트를 탐지해 `tcl` 데이터를 포함(다른 PC에서 tkinter 실패 방지)합니다.

---

## 새 프로젝트에 적용 순서(간단)

1. 프로젝트 루트에 `launcher.py`, `portable_entry.py`를 배치하고 `modules/`, `ui/` 구조를 준비합니다.
2. `.env.template` → `.env`로 복사 후 값 채움(키/시크릿 입력).
3. `requirements.txt` 기준으로 환경 구성: `python -m pip install -r requirements.txt`
4. 개발 실행 검증: `python -m streamlit run launcher.py`
5. (권장) 최소 스모크 테스트: `python -c "from modules.project_manager import ProjectManager; print('OK', ProjectManager)"`
5. 포터블 빌드: `powershell -ExecutionPolicy Bypass -File scripts/build_portable_exe_onedir.ps1`
6. `dist/<앱이름>/`에서 EXE 실행 검증(로그인, 파일 접근, 생성 파이프라인).

---

## 스모크 테스트(이식 직후 권장)

아래 명령들은 새 프로젝트로 이식한 직후, 가장 먼저 확인해야 하는 **import/경로/패키지 구조** 최소 검증입니다.

1) `modules.project_manager` import 확인

- `python -c "import modules.project_manager as pm; print('OK', pm.PROJECTS_DIR)"`
- `python -c "from modules.project_manager import ProjectManager; print('OK', ProjectManager)"`

2) (선택) Streamlit 엔트리 실행 확인

- `python -m streamlit run launcher.py`
