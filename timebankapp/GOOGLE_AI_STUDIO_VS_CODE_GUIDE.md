# Google AI Studio → VS Code(Windows) 로컬 개발 가이드 (Vite + React + TS)

이 문서는 Google AI Studio에서 내려받은 프론트엔드 프로젝트(예: Vite + React + TypeScript)를 **Windows PC의 VS Code에서 동일하게 실행**하고, **원본을 안전하게 수정**하며, 나중에 **다른 프로젝트로 재사용**하기 위해 알아야 할 핵심 포인트를 정리합니다.

---

## 0) 이 프로젝트의 정체(중요)

이 프로젝트는 “단일 HTML”이 아니라 다음 요소들이 결합된 **Vite 기반 React 앱**입니다.

- `index.html` : 브라우저가 처음 로드하는 엔트리 HTML
- `index.tsx` : React 앱 엔트리(번들러가 TSX → JS로 변환)
- `App.tsx` + `components/*` : 화면 구성 컴포넌트
- `vite.config.ts` : 개발 서버/빌드 설정(포트 등)

따라서 `python -m http.server` 같은 “정적 파일 서버”로는 TSX를 변환해줄 수 없어서 화면이 깨지거나(또는 배경만) 나옵니다.

---

## 1) 필수 설치(Windows)

- **Node.js LTS** 설치 권장(최신 LTS)
  - 설치 후 CMD/PowerShell에서 버전 확인:
    - `node -v`
    - `npm -v`
- **VS Code** 설치

---

## 2) VS Code에서 프로젝트 열기

1. VS Code → **File > Open Folder…**
2. 프로젝트 폴더(예: `d:\coding 2025\saletoile.com`) 선택
3. VS Code 터미널 열기: **Terminal > New Terminal**

---

## 3) 최초 1회: 의존성 설치

PowerShell 또는 CMD에서:

- `npm install`

설치가 끝나면 `node_modules/`와 `package-lock.json`이 생성/갱신됩니다.

---

## 4) 환경변수(API Key) 설정

이 프로젝트에는 `.env.local` 파일이 있고, 아래처럼 Gemini 키를 읽습니다.

- 파일: `.env.local`
- 키: `GEMINI_API_KEY`

예:

```dotenv
GEMINI_API_KEY=YOUR_REAL_KEY
```

주의:
- `.env.local`은 보통 git에 커밋하지 않습니다(비밀키 보호).
- 키가 없더라도 “정적 섹션”은 보일 수 있지만, Gemini 호출이 필요한 기능은 동작하지 않을 수 있습니다.

---

## 5) 로컬에서 실행(정답 루트)

### 개발 서버 실행

- `npm run dev`

정상이라면 터미널에 예를 들어 아래가 출력됩니다.

- `Local: http://localhost:7000/`

> 이 저장소는 `vite.config.ts`에서 기본 포트를 7000으로 맞춰둔 상태입니다.

### 브라우저 접속

- `http://localhost:7000/`

### 매우 흔한 실수 2가지

1) **터미널을 닫아버림**
- 개발 서버가 꺼지면 브라우저는 `ERR_CONNECTION_REFUSED`가 뜹니다.

2) **7000 포트를 다른 서버가 점유**
- 예: `python -m http.server 7000`을 켜두면 Vite가 못 떠서 화면이 깨집니다.

포트 점유 확인(PowerShell):

- `Get-NetTCPConnection -LocalPort 7000 -State Listen`

---

## 6) 배포용 빌드 & 로컬 미리보기

### 빌드

- `npm run build`

### 빌드 결과 미리보기(정적 배포와 유사)

- `npm run preview`

> preview는 개발서버와 다르게 “빌드 산출물”을 보여줍니다. 배포 전 확인용입니다.

---

## 7) 원본을 기반으로 수정할 때 반드시 알아야 할 요소

### A. “HTML만 수정”하면 끝나는 프로젝트가 아님

- 실제 화면 대부분은 `App.tsx`와 `components/*`에서 렌더링됩니다.
- `index.html`은 React를 마운트할 `<div id="root"></div>`와 엔트리 스크립트만 제공하는 역할이 큽니다.

수정 위치 가이드:
- 문구/레이아웃 변경: `components/*.tsx` 또는 `App.tsx`
- 전역 네비게이션/섹션 이동: `components/Navbar.tsx` 등
- 다국어/언어 전환: `contexts/LanguageContext.tsx`

### B. “정적 서버(Python)”로는 TSX가 실행되지 않음

- TSX/JSX는 브라우저가 직접 실행 못 합니다.
- Vite(또는 다른 번들러)가 변환/번들링해야 합니다.

즉, 로컬 확인은 원칙적으로:
- `npm run dev` (개발)
- `npm run build` + `npm run preview` (배포 유사)

### C. Tailwind 사용 방식

현재 `index.html`은 Tailwind CDN을 로드합니다.

- 장점: 별도 설정 없이 빠르게 스타일 적용
- 주의: Tailwind CDN은 개발/데모에 편하고, 제품 환경에서는 보통 PostCSS 기반(Tailwind 정식 설치)을 권장합니다.

> 이 프로젝트는 “AI Studio에서 내려받은 형태”를 존중해서 CDN 방식을 유지할 수 있고, 추후 필요하면 Tailwind를 정식 설치로 전환할 수 있습니다.

### D. 포트/호스트 설정

- 파일: `vite.config.ts`
- 기본 포트가 7000으로 맞춰져 있습니다.
- 환경변수로 오버라이드 가능하도록 되어 있습니다:
  - `PORT` 또는 `VITE_PORT`

예: `.env.local`에 추가

```dotenv
VITE_PORT=7000
```

---

## 8) 이미지/에셋을 “로컬에서” 제대로 다루는 방법

이 저장소에는 `Saletoile_img/` 폴더가 있습니다.

Vite/React에서 이미지 경로를 안정적으로 관리하는 방법은 크게 2가지입니다.

### 방법 1) `public/`로 두고 URL로 참조(가장 단순)

1. 이미지들을 `public/` 폴더로 이동(또는 복사)
2. 코드에서 `/이미지파일명`으로 참조

예:

```tsx
<img src="/hero.jpg" alt="..." />
```

장점: 경로가 단순하고, TS/번들 설정 영향을 덜 받음

### 방법 2) 컴포넌트에서 import로 번들링(권장 패턴)

1. 예: `src/assets/hero.jpg`에 두기
2. TSX에서 import 후 사용

```tsx
import heroImage from './assets/hero.jpg';

<img src={heroImage} alt="..." />
```

장점: 사용처 추적이 쉽고, 빌드 산출물에 안전하게 포함

---

## 9) “AI Studio에서 생성된 HTML을 다른 프로젝트에서 재사용”하는 방법

재사용 방식은 2가지 갈래로 나뉩니다.

### A) React/Vite 프로젝트에서 재사용(추천)

이 프로젝트의 설계는 React 컴포넌트 기반이므로, 가장 자연스러운 재사용은:

- `components/` 폴더(및 `contexts/`)를 새 프로젝트로 복사
- `App.tsx`의 섹션 구성/라우팅 방식만 새 프로젝트에 맞게 조정
- `package.json`의 의존성(react, lucide-react 등) 맞추기

권장 절차:
1. 새 Vite React TS 프로젝트 생성
2. 컴포넌트/컨텍스트 파일 복사
3. 이미지/정적 파일(`public` 또는 `assets`) 정리
4. `npm install` 후 `npm run dev`

### B) “순수 HTML/CSS/JS”로 재사용(주의)

AI Studio 결과가 React/TSX를 포함한다면, 순수 HTML로만 옮기려면:
- React 컴포넌트 구조를 HTML로 “펼쳐서” 재작성해야 하며
- 상태/이벤트(언어 토글 등)도 별도 JS로 다시 구현해야 합니다.

즉, **재사용 비용이 급격히 증가**합니다.

결론:
- 같은 계열(React/Vite) 프로젝트로 가져가는 것을 추천합니다.

---

## 10) 트러블슈팅(가장 자주 겪는 것)

### 증상: `ERR_CONNECTION_REFUSED`
- 원인: 개발서버가 꺼져있음(터미널 종료), 또는 포트가 막힘
- 해결:
  - `npm run dev` 다시 실행
  - `Get-NetTCPConnection -LocalPort 7000 -State Listen`로 리슨 확인

### 증상: `Failed to load module script ... MIME type 'text/plain'`
- 원인: Vite가 아니라 Python 같은 정적 서버가 `/index.tsx`를 그대로 서빙
- 해결: Python 서버 종료 → `npm run dev`로 실행

### 증상: 포트 충돌
- 해결:
  - 다른 포트로 변경(예: `.env.local`에 `VITE_PORT=7001`)
  - 또는 점유 프로세스 종료

---

## 11) 최소 실행 체크리스트

- [ ] Node.js 설치됨 (`node -v`)
- [ ] 프로젝트 폴더에서 `npm install` 완료
- [ ] `.env.local`에 `GEMINI_API_KEY` 설정(필요 시)
- [ ] `npm run dev` 실행 중(터미널 닫지 않기)
- [ ] 브라우저에서 `http://localhost:7000/` 접속

---

## 부록) 이 저장소에서 중요한 파일들

- `package.json`: 실행/빌드 스크립트, 의존성
- `vite.config.ts`: 개발서버 포트/환경변수/빌드 설정
- `index.html`: 엔트리 HTML(React 마운트/스크립트 로드)
- `index.tsx`: React 엔트리
- `App.tsx`: 페이지 구성의 중심
- `components/*`: 섹션/레이아웃 컴포넌트
- `contexts/LanguageContext.tsx`: 언어/텍스트 전환
