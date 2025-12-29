# API Integration Guide for External Projects

> 이 문서는 CanvasToon_Builder의 이미지/비디오 생성 API를 다른 프로젝트에 통합하기 위한 가이드입니다.

---

## 📦 패키지 복사 체크리스트

### 필수 파일 리스트

#### 1. **환경 설정 파일**
```
📄 .env                           # API 키 설정 (아래 템플릿 참조)
📄 requirements.txt               # Python 의존성 (필요한 부분만 발췌)
```

#### 2. **Core 모듈** (선택적 - 필요한 경우만)
```
📁 modules/
   └─ aiml_manager.py            # AIML API 통합 매니저 (NanoBanana, Kling O1 포함)
```

#### 3. **테스트 파일** (3가지 API별)
```
📁 tests_api_history/
   ├─ test_z_image_custom.py           # ✅ Replicate: Z-Image Turbo
   ├─ test_kling_o1_debug.py           # ✅ AIML API: Kling Image O1
   ├─ test_aiml_i2i_nanobanana.py      # ✅ AIML API: NanoBanana
   └─ test_kling_mart_scenarios.py     # 추가 참고: Kling O1 시나리오 테스트
```

#### 4. **참고 문서**
```
📄 API_SPECS.md                   # API 엔드포인트 및 파라미터 스펙
📄 AIMLAPI I2I ORRY document.md   # AIML API I2I 상세 가이드
```

---

## 🔑 .env 설정 템플릿

다른 프로젝트 루트에 `.env` 파일을 생성하고 아래 내용을 입력하세요:

```dotenv
# [AIML API 설정] - NanoBanana, Kling O1 사용
AIML_API_KEY=your_aiml_api_key_here

# [Replicate API 설정] - Z-Image Turbo 사용
REPLICATE_API_TOKEN=your_replicate_api_token_here

# [선택] OpenAI 호환 모드 (AIML API를 OpenAI SDK로 사용)
OPENAI_API_KEY=your_aiml_api_key_here
OPENAI_BASE_URL=https://api.aimlapi.com/v1
```

### API 키 발급 방법
- **AIML API**: https://aimlapi.com/ 회원가입 → Dashboard → API Keys
- **Replicate**: https://replicate.com/ 회원가입 → Account Settings → API Tokens

---

## 🧪 3가지 API 사용 가이드

### 1️⃣ Replicate: Z-Image Turbo (Text-to-Image)

#### 모델 정보
- **Model ID**: `prunaai/z-image-turbo`
- **특징**: 초고속 이미지 생성 (4 inference steps), 9:16 세로 비율 지원
- **용도**: 빠른 프로토타이핑, 실시간 생성

#### 테스트 파일
```bash
python tests_api_history/test_z_image_custom.py
```

#### 핵심 코드 예제
```python
import replicate
import os
from dotenv import load_dotenv

load_dotenv()

# API 키 설정
replicate_token = os.getenv("REPLICATE_API_TOKEN")

# 이미지 생성 (9:16 세로 비율)
output = replicate.run(
    "prunaai/z-image-turbo",
    input={
        "prompt": "A hyper-realistic photograph of a girl with long black hair wearing a white hoodie",
        "width": 576,        # 9:16 세로 비율
        "height": 1024,
        "num_inference_steps": 4,
        "guidance_scale": 1.5
    }
)

# 결과 저장
if isinstance(output, list):
    image_url = output[0]
else:
    image_url = output

# URL을 파일로 저장
import requests
response = requests.get(image_url)
with open("result.png", "wb") as f:
    f.write(response.content)
```

#### 주요 파라미터
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `prompt` | string | 생성할 이미지 설명 (영어) | Required |
| `width` | int | 이미지 너비 (576 권장) | 576 |
| `height` | int | 이미지 높이 (1024 권장) | 1024 |
| `num_inference_steps` | int | 생성 반복 횟수 (4~8) | 4 |
| `guidance_scale` | float | 프롬프트 충실도 (1.0~2.0) | 1.5 |

---

### 2️⃣ AIML API: Kling Image O1 (Image-to-Image Collage)

#### 모델 정보
- **Model ID**: `klingai/image-o1`
- **특징**: 다중 캐릭터 이미지를 하나의 장면으로 합성 (I2I Collage)
- **용도**: 캐릭터 조합 장면, 그룹 샷

#### 테스트 파일
```bash
python tests_api_history/test_kling_o1_debug.py
```

#### 핵심 코드 예제
```python
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AIML_API_KEY")
BASE_URL = "https://api.aimlapi.com/v1/images/generations"

def encode_image(image_path):
    """이미지를 Base64 Data URI로 변환"""
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"

# 여러 캐릭터 이미지를 리스트로 인코딩
char_images = ["char1.png", "char2.png", "char3.png"]
image_urls = [encode_image(img) for img in char_images]

# Kling O1 I2I 요청
payload = {
    "model": "klingai/image-o1",
    "prompt": "3 characters camping at night under starry sky. Cinematic shot, 8k, detailed.",
    "image_urls": image_urls,  # ⚠️ 리스트 형태 필수!
    "aspect_ratio": "16:9",    # 가로 비율
    "n": 1
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(BASE_URL, headers=headers, json=payload)
result = response.json()

# 결과 이미지 URL 추출
if 'data' in result:
    image_url = result['data'][0]['url']
    # URL에서 이미지 다운로드
    img_response = requests.get(image_url)
    with open("kling_result.png", "wb") as f:
        f.write(img_response.content)
```

#### 주요 파라미터
| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | `"klingai/image-o1"` 고정 |
| `prompt` | string | 장면 설명 (영어, 디테일 중요) |
| `image_urls` | array | Base64 Data URI 리스트 (최대 3~5개) |
| `aspect_ratio` | string | `"9:16"` 또는 `"16:9"` |
| `n` | int | 생성 이미지 개수 (기본 1) |

#### ⚠️ 주의사항
- **`image_url`(단수) 아님!** → **`image_urls`(복수) 배열 필수**
- Base64 Data URI 형식: `"data:image/png;base64,iVBORw0KG..."`
- 프롬프트는 캐릭터별 설명보다 **전체 장면 분위기** 중심으로 작성

---

### 3️⃣ AIML API: NanoBanana (Image-to-Image Edit)

#### 모델 정보
- **Model ID**: `google/nano-banana-pro-edit`
- **특징**: 원본 이미지 유지하며 프롬프트로 변형 (I2I Edit)
- **용도**: 캐릭터 포즈/배경 변경, 스타일 변환

#### 테스트 파일
```bash
python tests_api_history/test_aiml_i2i_nanobanana.py
```

#### 핵심 코드 예제
```python
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AIML_API_KEY")
BASE_URL = "https://api.aimlapi.com/v1/images/generations"

def encode_image_to_base64(image_path):
    """이미지를 Base64 Data URI로 변환"""
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    # 확장자에 따라 MIME 타입 설정
    ext = os.path.splitext(image_path)[1].lower().replace('.', '')
    if ext == 'jpg':
        ext = 'jpeg'
    return f"data:image/{ext};base64,{encoded}"

# 원본 이미지 인코딩
original_image = "character.png"
data_url = encode_image_to_base64(original_image)

# NanoBanana I2I Edit 요청
payload = {
    "model": "google/nano-banana-pro-edit",
    "prompt": "The character cleaning inside a supermarket, holding a mop, realistic texture, 8k",
    "image_urls": [data_url],  # 배열 형태
    "aspect_ratio": "9:16",     # 세로 비율
    "strength": 0.7,            # 원본 유지 강도 (0.5~0.9)
    "n": 1
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(BASE_URL, headers=headers, json=payload)
result = response.json()

# 결과 저장
if 'data' in result:
    image_url = result['data'][0]['url']
    img_response = requests.get(image_url)
    with open("nanobanana_result.png", "wb") as f:
        f.write(img_response.content)
```

#### 주요 파라미터
| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | `"google/nano-banana-pro-edit"` 고정 |
| `prompt` | string | 변형할 요소 설명 (영어) |
| `image_urls` | array | 원본 이미지 Base64 Data URI (1개) |
| `aspect_ratio` | string | `"9:16"`, `"16:9"`, `"1:1"` |
| `strength` | float | 원본 유지도 (0.5=많이 변형, 0.9=약간 변형) |
| `n` | int | 생성 이미지 개수 |

#### ⚠️ 주의사항
- `strength` 값이 낮을수록 프롬프트 영향 크고 원본에서 멀어짐
- 0.7~0.8 권장 (캐릭터 정체성 유지하며 배경/포즈 변경)

---

## 🔧 필수 Python 패키지

외부 프로젝트에서 아래 패키지를 설치하세요:

```bash
pip install replicate requests pillow python-dotenv openai
```

**최소 requirements.txt**:
```txt
replicate>=0.25.0
requests>=2.31.0
pillow>=10.0.0
python-dotenv>=1.0.0
openai>=1.12.0  # AIML API를 OpenAI SDK로 사용할 경우
```

---

## 📊 API 비교표

| API | 모델 | 타입 | 속도 | 품질 | 비용 | 용도 |
|-----|------|------|------|------|------|------|
| **Replicate Z-Image** | prunaai/z-image-turbo | T2I | ⚡️ 매우 빠름 (4 steps) | ⭐️⭐️⭐️ 보통 | 💰 저렴 | 빠른 프로토타입 |
| **AIML Kling O1** | klingai/image-o1 | I2I Collage | 🐢 느림 (60~120초) | ⭐️⭐️⭐️⭐️⭐️ 매우 높음 | 💰💰💰 비쌈 | 멀티 캐릭터 합성 |
| **AIML NanoBanana** | google/nano-banana-pro-edit | I2I Edit | ⚡️ 빠름 (20~30초) | ⭐️⭐️⭐️⭐️ 높음 | 💰💰 보통 | 캐릭터 변형/편집 |

---

## 🚀 Quick Start Workflow

### 시나리오 1: 단일 캐릭터 생성
```bash
# 1. Z-Image로 빠르게 생성
python tests_api_history/test_z_image_custom.py
```

### 시나리오 2: 캐릭터 배경 변경
```bash
# 2. NanoBanana로 I2I 편집
python tests_api_history/test_aiml_i2i_nanobanana.py
```

### 시나리오 3: 다중 캐릭터 합성
```bash
# 3. Kling O1로 멀티 캐릭터 콜라주
python tests_api_history/test_kling_o1_debug.py
```

---

## ⚠️ Troubleshooting

### 1. `REPLICATE_API_TOKEN not found`
- `.env` 파일에 `REPLICATE_API_TOKEN=your_token_here` 추가
- `load_dotenv()` 호출 확인

### 2. `AIML_API_KEY not found`
- `.env` 파일에 `AIML_API_KEY=your_key_here` 추가
- API 키 유효성 확인 (https://aimlapi.com/dashboard)

### 3. Kling O1 `image_url vs image_urls` 오류
```json
// ❌ 잘못된 방식
{"image_url": "data:image/png;base64,..."}

// ✅ 올바른 방식
{"image_urls": ["data:image/png;base64,...", "data:image/png;base64,..."]}
```

### 4. Base64 인코딩 오류
- Data URI 형식 확인: `"data:image/png;base64,iVBORw0KG..."`
- 파일 확장자에 맞는 MIME 타입 사용 (png/jpeg)

---

## 📚 추가 참고 자료

### 프로젝트 내 문서
- **API_SPECS.md**: 전체 API 엔드포인트 및 파라미터 스펙
- **AIMLAPI I2I ORRY document.md**: AIML API I2I 상세 가이드
- **tests_api_history/**: 다양한 API 조합 테스트 예제

### 외부 문서
- **AIML API Docs**: https://docs.aimlapi.com/
- **Replicate Docs**: https://replicate.com/docs
- **Z-Image Turbo**: https://replicate.com/prunaai/z-image-turbo
- **Kling Image O1**: https://docs.aimlapi.com/api-overview/image-models/kling

---

## 🎯 ROO CODE 학습 포인트

> AI 개발 에이전트(ROO CODE)가 이 가이드를 학습할 때 주의할 점:

### 1. **API 키 보안**
- `.env` 파일은 절대 Git에 커밋하지 않음
- `.gitignore`에 `.env` 추가 필수

### 2. **파라미터 타입 엄격 검증**
- `image_urls`는 **반드시 배열** (Kling O1, NanoBanana)
- `aspect_ratio`는 문자열 (`"9:16"`, `"16:9"`)
- Base64 Data URI는 `"data:image/...;base64,..."` 형식

### 3. **에러 핸들링**
- API 응답 `status_code` 확인 (200/201 성공)
- `response.json()`에서 `data` 또는 `output` 키 존재 여부 검증
- Timeout 설정 (Kling O1은 120초 이상 권장)

### 4. **최소 변경 원칙**
- 테스트 파일 복사 시 API 키만 `.env`로 분리
- 기존 로직(Base64 인코딩, 파일 저장) 유지
- 프롬프트 엔지니어링 패턴 보존

### 5. **의존성 최소화**
- `replicate`, `requests`, `pillow`, `python-dotenv`만 필수
- `aiml_manager.py`는 프로젝트 통합 시에만 사용 (선택적)

---

## 📋 체크리스트 (외부 프로젝트 이전 시)

- [ ] `.env` 파일 생성 및 API 키 입력
- [ ] `requirements.txt` 설치 (`pip install -r requirements.txt`)
- [ ] 테스트 파일 3개 복사
  - [ ] `test_z_image_custom.py`
  - [ ] `test_kling_o1_debug.py`
  - [ ] `test_aiml_i2i_nanobanana.py`
- [ ] `.gitignore`에 `.env` 추가
- [ ] 각 테스트 파일 실행 및 결과 확인
- [ ] (선택) `aiml_manager.py` 통합 (고급 사용)

---

**문서 버전**: v1.0  
**최종 업데이트**: 2025-12-28  
**작성자**: CanvasToon_Builder Team
