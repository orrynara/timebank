 Gemini Developer API + GenAI Python SDK 기준으로만 정리한 .md 템플릿이다.
​
모델: Nano Banana Pro (gemini-3-pro-image-preview) / Gemini 2.5 Flash Image (gemini-2.5-flash-image) / Veo 3.1 (veo-3.1-*-generate-preview) 기준.
​

text
# Google Gemini 이미지·영상 생성 API 정리 (Developer API 전용)

본 문서는 Google AI Studio / Gemini Developer API를 사용하는 **직접 호출용 매뉴얼**이다.  
Vertex AI, GCP 프로젝트/서비스계정 등은 전혀 사용하지 않는 구성을 전제로 한다.[web:130][web:133]

---

## 0. 공통 설정

### 0.1 인증 및 SDK

- 필요 요소  
  - Google 계정  
  - Google AI Studio에서 발급한 **Gemini API Key** 1개[web:39][web:40]  
- Python SDK  
  - 패키지: `google-genai` (공식 Gen AI Python SDK)[web:80][web:86][web:92]  
  - 설치:
    ```
    pip install google-genai python-dotenv
    ```

### 0.2 .env 예시

GEMINI_API_KEY=your_google_ai_studio_api_key_here

text

### 0.3 클라이언트 초기화 공통 코드

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)

text

이 `client`를 그대로 재사용하면서 **모델 이름만 바꿔 호출**하면 된다.[web:80][web:86][web:92]

---

## 1. Nano Banana Pro (Gemini 3 Pro Image)

### 1.1 개요

- 모델 ID: `gemini-3-pro-image-preview`[web:150]  
- 포지션: **최고 품질 이미지 생성** 모델 (디테일·구도·컨트롤 중시).[web:150]  
- 입력/출력: 텍스트 → 이미지, 이미지+텍스트 → 이미지.[web:13][web:150]

### 1.2 비용 & 속도 (대략)

- 공식 가격 구조: **토큰 기반 과금**, 이미지 하나당 약 수천 output tokens를 사용.[web:150][web:152]  
- 외부 분석 기준:  
  - 4K 이미지 기준 약 **0.2~0.24 USD / 이미지** 수준으로 추정.[web:151]  
  - AI Studio 무료 티어에서 일일 수백~수천 장까지 무료 제공(시점·플랜에 따라 상이).[web:151][web:152]  
- 지연 시간(비공식 벤치마크):  
  - 1K~2K 해상도 기준 **2~5초대 응답**이 일반적.[web:151][web:153]  

> 정확한 최신 요금은 반드시 공식 가격 페이지 확인:  
> https://ai.google.dev/gemini-api/docs/pricing[web:152]

### 1.3 Python 샘플 코드 (텍스트 → 이미지)

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import base64

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)

MODEL_ID = "gemini-3-pro-image-preview"

prompt = "롯데월드에서 솜사탕을 들고 있는 kpop 여자 아이돌, 16:9, 고해상도, 자연스러운 조명, 사진 스타일"

result = client.models.generate_content(
model=MODEL_ID,
contents=prompt,
config=types.GenerateContentConfig(
response_modalities=[types.Modality.IMAGE],
aspect_ratio="16:9", # 지원되는 경우에만 적용
),
)

첫 번째 이미지 추출
img_part = result.candidates.content.parts.inline_data
img_bytes = base64.b64decode(img_part.data)

output_path = r"D:\coding 2025\timebank\assets\generated\nanobanana_pro_lotteworld.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "wb") as f:
f.write(img_bytes)

print("saved:", output_path)

text

### 1.4 주요 파라미터 사용법

- `model="gemini-3-pro-image-preview"`: Nano Banana Pro 모델 지정.[web:150]  
- `contents=prompt`: 문자열 또는 `Content` 배열. 단일 텍스트면 문자열로 충분.[web:80]  
- `response_modalities=[Modality.IMAGE]`: 이미지 응답만 받도록 지정.[web:80][web:95]  
- `aspect_ratio`: `"16:9"`, `"1:1"` 등 지원 비율. 지원 여부는 모델 문서 참조.[web:89][web:150]  

---

## 2. Gemini 2.5 Flash Image (Nano Banana)

### 2.1 개요

- 모델 ID: `gemini-2.5-flash-image`[web:50][web:87]  
- 포지션: **저지연·저비용 이미지 생성**에 특화된 경량/고속 모델.[web:87][web:93]  
- 용도: 실시간 미리보기, 대량 생성, UX 중시 시나리오.[web:87][web:156]

### 2.2 비용 & 속도 (대략)

- 가격(공식 구조):  
  - output tokens 기준 **약 30 USD / 1M tokens**,  
  - 1장당 약 0.039 USD 정도로 분석.[web:87][web:152][web:156]  
- 속도:  
  - 1024×1024 기준 평균 **3~5초**.[web:153][web:156]  
- 무료 티어: AI Studio에서 일간 무료 호출량 제공 (정책에 따라 변동).[web:152][web:153]

### 2.3 Python 샘플 코드

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import base64

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)

MODEL_ID = "gemini-2.5-flash-image"

prompt = "롯데월드에서 솜사탕을 들고 있는 kpop 여자 아이돌, 16:9, 산뜻한 색감, SNS용 썸네일 스타일"

result = client.models.generate_content(
model=MODEL_ID,
contents=prompt,
config=types.GenerateContentConfig(
response_modalities=[types.Modality.IMAGE],
aspect_ratio="16:9",
),
)

img_part = result.candidates.content.parts.inline_data
img_bytes = base64.b64decode(img_part.data)

output_path = r"D:\coding 2025\timebank\assets\generated\flash_image_lotteworld.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "wb") as f:
f.write(img_bytes)

print("saved:", output_path)

text

### 2.4 주요 파라미터 사용법

- `model="gemini-2.5-flash-image"`: Nano Banana (Fast) 모델 지정.[web:50][web:87]  
- 나머지 구조는 Pro와 동일 (`contents`, `response_modalities`, `aspect_ratio` 등).[web:80][web:93]  

---

## 3. Veo 3.1 (영상 생성)

### 3.1 개요

- 모델 ID(예시):  
  - 표준: `veo-3.1-generate-preview`  
  - Fast: `veo-3.1-fast-generate-preview` (문서 상 Fast 버전 존재).[web:95][web:159]  
- 기능: 텍스트→비디오, 이미지→비디오, 비디오 확장 등.[web:95][web:118][web:120]  
- 길이: 수 초 ~ 최대 141초까지 Veo 생성 영상 지원.[web:95]

### 3.2 비용 & 속도 (대략)

Gemini Developer API 가격표 기준:[web:152]

- **Veo 3 / Veo 3.1** (표준, 3.x 기준 유사 구조)  
  - Standard: **0.40 USD / 1초**[web:152]  
  - Fast: **0.15 USD / 1초**[web:152]  
- 예: 8초 Standard 비디오 1개  
  - 대략 3.2 USD 수준(세부 정책/할인, 미리보기 여부에 따라 달라질 수 있음).[web:152]  
- 요청 지연 시간  
  - 공식 문서: 최소 11초 ~ 최대 6분 (길이·해상도·부하에 따라 편차).[web:95]  

> 최신 가격 및 길이/해상도 제한은 여기 확인:  
> https://ai.google.dev/gemini-api/docs/pricing[web:152]  
> https://ai.google.dev/gemini-api/docs/video[web:95]

### 3.3 Python 샘플 코드 (텍스트 → 비디오)

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import base64

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)

MODEL_ID = "veo-3.1-generate-preview"

prompt = (
"롯데월드에서 솜사탕을 들고 있는 kpop 여자 아이돌이 "
"카메라를 향해 천천히 걸어오는 16:9 영상, 자연스러운 조명, "
"영화 같은 카메라 무빙, 짧은 인트로 샷"
)

operation = client.models.generate_videos(
model=MODEL_ID,
prompt=prompt,
config=types.GenerateVideosConfig(
# 예시 값: 720p, 8초짜리 한 개 비디오
resolution="RESOLUTION_720P",
number_of_videos=1,
duration_seconds=8,
),
)

장기 실행 작업 완료 대기
result = operation.result()

video_bytes = base64.b64decode(result.videos.video_bytes)

output_path = r"D:\coding 2025\timebank\assets\generated\veo31_lotteworld.mp4"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "wb") as f:
f.write(video_bytes)

print("saved:", output_path)

text

> 주: 실제 필드 이름(`video_bytes`, `videos[0]` 구조)은 문서/SDK 버전에 따라 약간 달라질 수 있으므로, 항상 공식 예제 확인 필요.[web:95][web:118]

### 3.4 Python 샘플 코드 (이미지 → 비디오)

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import base64

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)

MODEL_ID = "veo-3.1-generate-preview"

INPUT_IMAGE_PATH = r"D:\coding 2025\timebank\assets\generated\flash_image_lotteworld.png"
OUTPUT_VIDEO_PATH = r"D:\coding 2025\timebank\assets\generated\veo31_lotteworld_from_image.mp4"

with open(INPUT_IMAGE_PATH, "rb") as f:
image_bytes = f.read()

prompt = (
"입력 이미지를 기반으로, 같은 여자 아이돌이 롯데월드 배경에서 "
"카메라를 향해 천천히 걸어오는 16:9 영상, 자연스러운 조명, 영화 같은 느낌"
)

operation = client.models.generate_videos(
model=MODEL_ID,
prompt=prompt,
image=types.GenerateVideosImageInput(
mime_type="image/png",
data=image_bytes,
),
config=types.GenerateVideosConfig(
resolution="RESOLUTION_720P",
number_of_videos=1,
duration_seconds=8,
),
)

result = operation.result()

video_bytes = base64.b64decode(result.videos.video_bytes)

os.makedirs(os.path.dirname(OUTPUT_VIDEO_PATH), exist_ok=True)
with open(OUTPUT_VIDEO_PATH, "wb") as f:
f.write(video_bytes)

print("saved:", OUTPUT_VIDEO_PATH)

text

### 3.5 주요 파라미터 사용법

- `model="veo-3.1-generate-preview"`  
  - Standard 품질의 Veo 3.1 프리뷰 모델.[web:95][web:122]  
- `prompt`  
  - 영상 내용 설명 (장면, 카메라 무빙, 조명, 스타일 등).[web:95][web:113]  
- `image=GenerateVideosImageInput(...)`  
  - 이미지→비디오 모드에서 참조 이미지 입력.[web:95][web:126]  
- `GenerateVideosConfig`  
  - `resolution`: `"RESOLUTION_720P"`, `"RESOLUTION_1080P"` 등.[web:96][web:121]  
  - `number_of_videos`: 생성할 클립 수.  
  - `duration_seconds`: 초 단위 길이 (제약 범위는 문서 참조).[web:95][web:96]  

---

## 4. 요약 테이블

### 이미지/영상 모델 개요 비교

| 항목 | Nano Banana Pro<br/>(gemini-3-pro-image-preview) | Gemini 2.5 Flash Image<br/>(gemini-2.5-flash-image) | Veo 3.1<br/>(veo-3.1-generate-preview) |
|------|--------------------------------------------------|-----------------------------------------------------|----------------------------------------|
| 타입 | 고품질 이미지 | 고속/저비용 이미지 | 동영상 (텍스트·이미지→비디오) |
| 주요 용도 | 프로덕션급 고퀄리티, 디테일 작업 | 실시간/대량 썸네일, UX | 숏폼·시네마틱 영상 생성 |
| 과금 방식 | 토큰 기반, 이미지당 수십~수백 센트 수준 | 토큰 기반, 이미지당 약 0.04 USD | 초당 과금(0.40/0.15 USD/초) |
| 평균 응답 | 수초(해상도에 따라 2~5초) | 수초(평균 3~5초) | 10초~수분(길이·해상도에 따라) |
| 입력 | 텍스트, 이미지+텍스트 | 텍스트, 이미지+텍스트 | 텍스트, 이미지, 비디오+텍스트 |

> 정확한 단가/쿼터는 항상 최신 공식 문서 기준으로 재확인 필요:  
> https://ai.google.dev/gemini-api/docs/pricing[web:152]

---

이 `.md`를 그대로 플랫폼 레포에 넣고,  
- 모델 선택 UI에서 `model` 값만 바인딩  
- 프롬프트/옵션을 `GenerateContentConfig`, `GenerateVideosConfig` 형태로 매핑  
하는 방식으로 쓰면 재사용성이 좋을 것이다.[web:80][web:95][web:150]