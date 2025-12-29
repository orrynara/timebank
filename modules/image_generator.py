"""Google GenAI(Gemini) 기반 이미지 및 비디오 생성 모듈.

Gemini Pro Vision(이미지) 및 Veo 3.1(비디오) 모델을 사용하여
배경 이미지와 프로모션 영상을 생성합니다.
"""

import os
import time
import requests
from pathlib import Path
from datetime import datetime
from google import genai
from google.genai.types import GenerateContentConfig, Modality, GenerateVideosConfig
from google.genai import types # Veo용
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image

# .env 로드
load_dotenv()

# 상수 정의
GENERATED_DIR = Path("assets/generated")
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

MODEL_IMAGE = "gemini-3-pro-image-preview"
MODEL_VIDEO = "veo-3.1-generate-preview"

class ImageGenerator:
    """Google GenAI 기반 이미지/비디오 생성 클래스."""

    def __init__(self):
        # 인증 로직 동기화: GEMINI_API_KEY 우선, 없으면 GOOGLE_API_KEY 확인
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            google_key = os.getenv("GOOGLE_API_KEY")
            if google_key:
                print("[WARN] GEMINI_API_KEY not found; using GOOGLE_API_KEY instead.")
                self.api_key = google_key
            else:
                print("⚠️ GEMINI_API_KEY가 설정되지 않았습니다.")
                self.client = None
                return

        self.client = genai.Client(api_key=self.api_key)

    def _extract_first_inline_image_bytes(self, response):
        """응답에서 인라인 이미지 바이트 추출 (테스트 코드 로직 이식)"""
        candidates = getattr(response, "candidates", None) or []
        if not candidates:
            raise ValueError("No candidates in response")

        content = getattr(candidates[0], "content", None)
        parts = getattr(content, "parts", None) or []
        if not parts:
            raise ValueError("No parts in first candidate content")

        for part in parts:
            inline_data = getattr(part, "inline_data", None)
            if inline_data is None:
                continue

            data = getattr(inline_data, "data", None)
            if data:
                return data

        raise ValueError("No inline image data found in response parts")

    def generate_image(self, prompt: str, filename_prefix: str) -> str:
        """
        Gemini 모델을 사용하여 이미지를 생성합니다.
        
        Args:
            prompt: 이미지 생성 프롬프트
            filename_prefix: 저장될 파일명 접두사 (예: region_id)
            
        Returns:
            저장된 파일의 로컬 경로 (str) 또는 None
        """
        if not self.client:
            print("⚠️ Client가 초기화되지 않아 이미지를 생성할 수 없습니다.")
            return None

        # NanoBanana Framework 스타일 프롬프트 구성
        full_prompt = (
            "Subject: A futuristic organic-shaped glamping pod with a sleek white polymer shell "
            "and floor-to-ceiling panoramic glass windows. "
            "Action: glowing warmly from the inside, nestled peacefully on a modern wooden deck. "
            f"Environment: surrounded by {prompt if prompt else 'nature'}, creating a serene atmosphere. "
            "Art Style: Professional architectural photography, photorealistic, 8k resolution, cinematic composition. "
            "Lighting: Soft golden hour sunlight filtering through the canopy, volumetric lighting. "
            "Details: intricate textures of polished glass and morning dew, shot on Sony A7R IV, 35mm lens, sharp focus, ultra-detailed."
        )

        try:
            print(f"🚀 이미지 생성 요청 (Model: {MODEL_IMAGE})...")
            
            # 테스트 코드와 동일한 방식(generate_content + response_modalities=[IMAGE]) 사용
            response = self.client.models.generate_content(
                model=MODEL_IMAGE,
                contents=[full_prompt],
                config=GenerateContentConfig(response_modalities=[Modality.IMAGE]),
            )

            # 데이터 추출
            image_bytes = self._extract_first_inline_image_bytes(response)
            
            # 파일 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.png"
            filepath = GENERATED_DIR / filename
            
            # PIL로 저장
            img = Image.open(BytesIO(image_bytes))
            img.save(filepath, format="PNG")
                
            print(f"✅ 이미지 저장 완료: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"❌ 이미지 생성 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            raise e # 상위(UI)로 에러 전파하여 화면에 표시

    def generate_video(self, image_path: str, prompt: str) -> str:
        """
        Veo 3.1 모델을 사용하여 이미지 기반 비디오를 생성합니다.
        
        Args:
            image_path: 원본 이미지 경로 (str)
            prompt: 비디오 생성 프롬프트 (카메라 무빙 등)
            
        Returns:
            저장된 비디오 파일의 로컬 경로 (str) 또는 None
        """
        if not self.client:
            print("⚠️ Client가 초기화되지 않아 비디오를 생성할 수 없습니다.")
            return None
            
        if not os.path.exists(image_path):
            print(f"❌ 원본 이미지를 찾을 수 없습니다: {image_path}")
            return None

        try:
            print(f"Reading image: {image_path}")
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            # types.Image 객체 생성
            image_input = types.Image(
                image_bytes=image_bytes,
                mime_type="image/png" # PNG라고 가정
            )

            print(f"🚀 비디오 생성 요청 (Model: {MODEL_VIDEO})...")
            print(f"Prompt: {prompt}")

            # Veo 3.1 호출
            response = self.client.models.generate_videos(
                model=MODEL_VIDEO,
                prompt=prompt,
                image=image_input,
                config=GenerateVideosConfig(
                    aspect_ratio="16:9"
                )
            )

            # LRO 폴링 및 결과 다운로드 로직 (test_veo31_from_image.py 참조)
            result = None
            
            # 1. 동기 응답인 경우
            if hasattr(response, 'generated_videos') and response.generated_videos:
                result = response
                print("Response has generated_videos directly.")
            
            # 2. 비동기 LRO(Long Running Operation)인 경우
            elif hasattr(response, 'name') and response.name:
                print(f"Operation Name: {response.name}")
                
                while True:
                    try:
                        print("Polling operation status...")
                        # SDK 버전에 따라 인자 방식이 다를 수 있어 안전하게 처리
                        op_status = self.client.operations.get(operation=response)
                        
                        if op_status.done:
                            if op_status.error:
                                error_msg = f"Operation failed with error: {op_status.error}"
                                print(error_msg)
                                raise Exception(error_msg) # 에러 전파
                            
                            result = op_status.result
                            if not result and op_status.response:
                                result = op_status.response
                            break
                        
                        time.sleep(5)
                    except Exception as poll_err:
                        print(f"Polling error: {poll_err}")
                        raise poll_err
            
            if not result:
                print("❌ 비디오 생성 실패 (결과 없음)")
                return None

            # 비디오 다운로드
            target_uri = None
            if hasattr(result, 'generated_videos') and result.generated_videos:
                for video in result.generated_videos:
                     if hasattr(video, 'video') and hasattr(video.video, 'uri') and video.video.uri:
                         target_uri = video.video.uri
                         break
                     elif hasattr(video, 'uri') and video.uri:
                         target_uri = video.uri
                         break
            
            if target_uri:
                print(f"Downloading video from: {target_uri}")
                
                # API Key 헤더 추가
                headers = {}
                if self.api_key:
                    headers["x-goog-api-key"] = self.api_key
                
                resp = requests.get(target_uri, headers=headers)
                
                if resp.status_code == 200:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"video_{timestamp}.mp4"
                    output_path = GENERATED_DIR / filename
                    
                    with open(output_path, "wb") as f:
                        f.write(resp.content)
                    
                    print(f"✅ 비디오 저장 완료: {output_path}")
                    return str(output_path)
                else:
                    error_msg = f"Download failed with status {resp.status_code}"
                    print(f"❌ {error_msg}")
                    raise Exception(error_msg)
            else:
                 print("❌ 결과에서 비디오 URI를 찾을 수 없습니다.")
                 return None

        except Exception as e:
            print(f"❌ 비디오 생성 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            raise e

# 싱글톤 인스턴스
image_gen = ImageGenerator()
