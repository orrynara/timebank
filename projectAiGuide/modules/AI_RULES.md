# AI 에이전트 행동 규칙 (AI Agent Behavior Rules) — CanvasToon Builder

이 문서는 본 프로젝트에서 AI 에이전트가 코드를 생성/수정할 때 반드시 따라야 하는 개발 표준(Development Standards)이다.
목표는 **안전(Safety)**, **재현성(Reproducibility)**, **일관성(Consistency)**, **유지보수성(Maintainability)** 을 최대화하는 것이다.

---

## 1. 코드 생성 정책 (Code Generation Policy) — 최우선(CRITICAL)
- **부분 수정 금지 (No Partial Edits):** 어떤 파일이든(특히 UI 파일) 수정 시 **부분 코드 조각(snippet)** 만 제공하지 않는다.
- **전체 재작성 (Full Rewrite):** 파일을 수정할 때는 `import`부터 마지막 줄까지 **파일 전체를 재생성(Full Rewrite)** 한다.
  - 이유: Streamlit 재실행(re-run) 환경에서 누락된 import, 끊긴 함수/변수 참조로 `NameError` 및 로직 단절이 빈번히 발생한다.
- **기능 보존 (Backward Compatibility):** 명시적으로 지시받지 않은 기존 기능은 삭제/축소/동작 변경을 금지한다.
- **최소 변경 (Minimal Change):** 목적 달성에 필요한 최소 범위만 수정한다(불필요한 리네이밍, 포맷 대변경 금지).

---

## 2. 격리 개발 환경 규칙 (Sandbox Development Rules)
신규 기능 개발은 반드시 **샌드박스(Sandbox)** 방식으로 진행한다.

- **독립 테스트 파일 생성:** 신규 기능은 먼저 `tests/` 폴더에 **독립 테스트 파일**을 만든다.
  - 기존 기능/파일을 건드리지 않고도 신규 로직을 검증할 수 있어야 한다.
- **로직 완결성 증명 후 이식:** 테스트 파일에서 로직의 입력/출력, 예외 케이스, 최소한의 성공 조건을 만족함을 확인한 뒤 `modules/`로 이식(Port)한다.
- **안전 우선 원칙 (Safety-First Principle):**
  - 신규 기능 검증은 “기존 기능을 변경하지 않는 방식”이 기본이다.
  - 기존 기능 변경이 불가피한 경우, 변경 이유/영향 범위를 명확히 하고 회귀(regression) 가능성을 최소화한다.

---

## 3. 테스트 이력 관리 (Test History Rules)
성공한 테스트(실행 성공 + 핵심 결과 확인)는 반드시 이력으로 남겨 재현성을 확보한다.

- **기록 파일:** `test_history_function_py.md`
- **기록 대상:** 신규 기능 개발/리팩터링/버그 수정과 관련된 “성공한 테스트”
- **필수 기록 항목(Template):**
  - `[날짜]` (YYYY-MM-DD)
  - `[테스트 파일명]` (예: `tests/test_xxx.py`)
  - `[함수명 및 파라미터]` (예: `func(arg1=..., arg2=...)`)
  - `[필요 환경 변수]` (예: `AIML_API_KEY`, `FIREBASE_KEY_PATH` 등)
  - `[성공 결과 요약]` (무엇이 검증되었는지 1~3문장)

---

## 4. 파일 구조 및 최적화 (File Structure & Optimization)
- **라인 제한 (Line Limit):** 한 파일은 가급적 **400~500 라인 이하**로 유지한다.
- **리팩터링 프로토콜 (Refactoring Protocol):**
  - 파일이 커지면 즉시 `modules/`로 로직을 분리하는 방안을 제안한다.
  - **참조 표준(Reference Standard):** `modules/project_manager.py`의 구조를 **분리 기준의 표준**으로 삼는다.
    - UI(뷰, View): 렌더링(`st.write`, `st.columns`, 입력 위젯) 중심
    - 모듈(로직, Logic): 데이터 처리, 상태 관리, 외부 연동, 비즈니스 규칙 중심
- **UI 파일 금지사항:** UI 파일에는 비즈니스 로직/복잡한 데이터 변환을 두지 않는다(필요 시 모듈로 이동).

---

## 5. 상태 관리 (State Management)
- **Streamlit 특성(Persistence):** Streamlit은 상호작용마다 스크립트를 재실행(re-run)한다.
- **선 로드(Load First):** `render()` 함수의 **가장 상단**에서 `load_data()` 또는 이에 준하는 로드 로직을 실행한다.
- **즉시 저장(Save Immediately):** 데이터 변경 직후 `save_data()` 또는 이에 준하는 저장 로직을 즉시 호출한다.
- **세션 키 일관성(Session State Keys):** 세션 상태 키(`st.session_state`)는 임의로 변경하지 말고, 필요 시 기존 키와 호환되게 확장한다.

---

## 6. 오류 처리 및 방어 코딩 (Error Handling & Defensive Coding)
- **직접 인덱싱 금지:** 딕셔너리 키를 직접 접근(`data['key']`)하지 않는다. 반드시 `data.get('key', default)`를 사용한다.
- **루트 원인 분석(Root Cause):** 증상만 가리는 패치보다, 누락된 초기화/상태 불일치 등 **근본 원인**을 먼저 분석한다.
- **실패 모드 명시(Failure Modes):** 외부 API/파일 I/O는 실패 가능성을 가정하고 예외 처리 및 사용자 피드백(에러 메시지)을 제공한다.

---

## 7. 모듈화/이식 규칙 (Module Porting Rules)
테스트에서 검증된 코드를 `modules/`로 옮길 때 다음을 준수한다.

- **구조 보존(Structure Preservation):** 기존 파일의 구조/흐름을 깨뜨리지 않는다.
- **참조 표준 준수:** `modules/project_manager.py`의 책임 분리(Separation of Concerns) 구조를 기준으로 모듈화한다.
- **시그니처 안정성(Stable Signatures):** 이미 사용 중인 함수/클래스 시그니처를 임의로 변경하지 않는다(필요 시 래퍼(wrapper)로 호환성 유지).

---

## 8. 언어 규칙 (Language & Localization)
- **한국어 우선(Korean-first):** 모든 규칙 설명, 주석(comments), UI 라벨(labels)은 **한국어**로 작성한다.
- **핵심 기술 용어 병기:** 필요한 경우 핵심 기술 용어는 한국어 뒤에 **영문(English)** 을 괄호로 병기한다.
