# Google GenAI 이미지/비디오(이미지→Veo 3.1) 이전 가이드

이 문서는 다른 프로젝트로 **이미지 생성(2개 모델)** 및 **Veo 3.1 이미지 기반 동영상 생성** 기능을 옮길 때, 그대로 따라 하면 재현되도록 정리한 가이드입니다.

대상 테스트 스크립트(현재 프로젝트 기준):
- 이미지 생성: `test_nano_flash_images.py`
- 이미지→비디오(Veo 3.1): `test_veo31_from_image.py`

---

## 1) 필요한 패키지

아래 패키지가 필요합니다.

- `google-genai`
- `python-dotenv`
- `pillow`
- `requests`

설치 예시(Windows PowerShell):

```powershell
pip install google-genai python-dotenv pillow requests
```

프로젝트가 venv를 사용한다면, 반드시 **해당 venv**에서 설치하세요.

---

## 2) 디렉터리/파일 구조 (권장)

아래는 “생성 결과물을 한 곳에 모으는” 가장 단순한 구조입니다.

```
<project-root>/
  .env
  assets/
    generated/
  test_nano_flash_images.py
  test_veo31_from_image.py
```

출력 폴더는 코드에서 `os.makedirs(..., exist_ok=True)`로 생성하도록 유지하는 것을 권장합니다.

---

## 3) 환경 변수(.env) 설정

### 필수 키
- `GEMINI_API_KEY` (권장)

현재 테스트 코드 동작 기준:
- `test_veo31_from_image.py`는 `GEMINI_API_KEY`가 **필수**입니다.
- `test_nano_flash_images.py`는 `GEMINI_API_KEY`가 없으면 `GOOGLE_API_KEY`로 대체하도록 작성돼 있습니다.

권장 `.env` 예시(값은 절대 커밋 금지):

```dotenv
GEMINI_API_KEY=YOUR_API_KEY_HERE
# (선택) 기존 프로젝트 호환용
GOOGLE_API_KEY=YOUR_API_KEY_HERE
```

보안 권장사항:
- `.env`는 `.gitignore`에 포함
- 로그/스크린샷에 키 노출 금지

---

## 4) 이미지 생성 테스트 (Nano Banana Pro / Flash Image)

### 사용 모델
- Nano Banana Pro: `model="gemini-3-pro-image-preview"`
- Gemini 2.5 Flash Image: `model="gemini-2.5-flash-image"`

### 공통 프롬프트
- "롯데월드에서 솜사탕을 들고 있는 kpop 여자 아이돌, 16:9, 고해상도, 자연스러운 조명, 사진 스타일"

### 저장 파일명
- `nanobanana_pro_lotteworld.png`
- `flash_image_lotteworld.png`

### 실행

```powershell
python test_nano_flash_images.py
```

성공 시 예시 로그:
- `saved: ...\assets\generated\nanobanana_pro_lotteworld.png`
- `saved: ...\assets\generated\flash_image_lotteworld.png`

구현 포인트(다른 프로젝트에서 재사용 시 핵심):
- `from google import genai`
- `GenerateContentConfig(response_modalities=[Modality.IMAGE])`
- `response.candidates[0].content.parts[*].inline_data.data`에서 bytes 추출
- `PIL.Image.open(BytesIO(...)).save(..., format="PNG")`

---

## 5) Veo 3.1 이미지 기반 동영상 생성 테스트

### 사용 모델
- Veo 3.1 Preview: `model="veo-3.1-generate-preview"`

### 입력/출력
- 입력 이미지: `assets/generated/flash_image_lotteworld.png`
- 출력 비디오: `assets/generated/veo31_lotteworld.mp4`

### 실행

```powershell
python test_veo31_from_image.py
```

### 구현 포인트(다른 프로젝트에서 재사용 시 핵심)

1) **이미지 입력 구성**
- `types.Image(image_bytes=..., mime_type="image/png")`

2) **비동기(LRO) 폴링**
- `client.models.generate_videos(...)`가 LRO(Operation)를 반환할 수 있음
- SDK의 `result()` 호환성 이슈가 있을 수 있어, 아래 방식으로 상태 확인:
  - `client.operations.get(operation=response)` (operation 객체 전달)
  - 보조 fallback: `client.operations.get(name=operation_name)`

3) **다운로드 시 403 방지**
- 생성된 video `uri`를 `requests.get()`로 받을 때 403이 날 수 있음
- 이때 API Key를 헤더로 전달:
  - `headers = {"x-goog-api-key": api_key}`

4) **저장**
- 다운로드 성공(HTTP 200)이면 `OUTPUT_VIDEO_PATH`에 mp4로 저장

---

## 6) 다른 프로젝트로 “이전” 체크리스트

- [ ] `google-genai`, `python-dotenv`, `pillow`, `requests` 설치
- [ ] `.env`에 `GEMINI_API_KEY` 설정 (권장: 단일 키로 통일)
- [ ] 출력 폴더 `assets/generated` 생성 로직 유지
- [ ] 방화벽/프록시 환경이면 다운로드 요청(URI)이 막히지 않는지 확인
- [ ] 403 발생 시 `x-goog-api-key` 헤더 다운로드 방식 유지

---

## 7) Roo Code(또는 다른 에이전트)에게 붙여넣을 이전 요청 문구

아래 문구 그대로 복사해서, 대상 프로젝트에서 작업하도록 요청하면 됩니다.

"""
다른 프로젝트에 Google GenAI 기반 미디어 생성 기능을 이식해줘.

요구사항:
1) google-genai / python-dotenv / pillow / requests 의존성 추가
2) .env에서 GEMINI_API_KEY를 읽어 genai.Client 초기화
3) 이미지 생성: gemini-3-pro-image-preview, gemini-2.5-flash-image 호출 후 inline image bytes를 PNG로 저장
4) Veo 3.1: veo-3.1-generate-preview로 이미지 기반 영상 생성. LRO는 client.operations.get(operation=response)로 폴링.
5) 결과 video uri 다운로드는 403 방지를 위해 requests.get(..., headers={"x-goog-api-key": api_key}) 사용
6) 결과물은 assets/generated/ 아래로 저장

참고: 현재 구현 예시는 timebank 프로젝트의 test_nano_flash_images.py, test_veo31_from_image.py와 동일하게 맞춰줘.
"""
