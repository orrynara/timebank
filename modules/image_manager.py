"""이미지 생성 및 관리 모듈.

AIML API(Kling O1, NanoBanana) 및 Replicate(Z-Image Turbo)를 사용하여
배경/풍경 이미지를 생성하고 관리합니다.
"""

import os
import time
import requests
import replicate
from pathlib import Path
from datetime import datetime

# .env 로드
from dotenv import load_dotenv
load_dotenv()

AIML_API_KEY = os.getenv("AIML_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# 이미지 저장 경로
GENERATED_DIR = Path("assets/generated")
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

class ImageGenerator:
    """이미지 생성 및 관리 클래스."""

    def __init__(self):
        pass
    
    def generate_image(self, prompt: str, filename_prefix: str) -> str:
        """
        프롬프트를 받아 이미지를 생성하고 로컬에 저장합니다.
        NanoBanana Framework 기반의 실사 프롬프트 구조를 적용합니다.
        
        Args:
            prompt: 사용자 입력 또는 기본 프롬프트 (NanoBanana 구조에 병합됨)
            filename_prefix: 저장될 파일명 접두사 (예: region_id)
            
        Returns:
            저장된 파일의 로컬 경로 (str) 또는 None
        """
        
        if not REPLICATE_API_TOKEN:
            print("⚠️ REPLICATE_API_TOKEN이 없습니다. 이미지 생성을 건너뜁니다.")
            return None

        # NanoBanana Framework 프롬프트 적용
        # 사용자의 입력(prompt)이 'Environment' 부분에 자연스럽게 녹아들도록 구성하거나,
        # 아래 구조를 기본으로 하되 prompt 내용을 반영.
        # 여기서는 지시사항에 따라 NanoBanana Framework 구조로 전면 교체하며, 
        # 사용자의 prompt(예: 양평의 숲) 정보를 Environment에 반영하는 형태로 구현.
        
        # 기본 양평 숲 프롬프트 (지시사항에 명시된 내용)
        nanobanana_prompt = (
            "Subject: A futuristic organic-shaped glamping pod with a sleek white polymer shell "
            "and floor-to-ceiling panoramic glass windows. "
            "Action: glowing warmly from the inside, nestled peacefully on a modern wooden deck. "
            f"Environment: surrounded by a dense ancient forest with tall misty trees and mossy rocks in {prompt if prompt else 'nature'}. "
            "Art Style: Professional architectural photography, photorealistic, 8k resolution, cinematic composition. "
            "Lighting: Soft golden hour sunlight filtering through the canopy, volumetric lighting. "
            "Details: intricate textures of polished glass and morning dew, shot on Sony A7R IV, 35mm lens, sharp focus, ultra-detailed."
        )

        try:
            print(f"🚀 이미지 생성 시작 (NanoBanana Framework): {nanobanana_prompt}")
            
            # Replicate API 호출 (Z-Image Turbo)
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={
                    "prompt": nanobanana_prompt,
                    "negative_prompt": "blurry, low quality, distortion, ugly, text, watermark, cartoon, illustration, painting",
                    "width": 1024,
                    "height": 768,
                    "num_inference_steps": 30
                }
            )
            
            # output은 보통 이미지 URL 리스트임
            if output and len(output) > 0:
                image_url = output[0]
                
                # 이미지 다운로드
                response = requests.get(image_url)
                if response.status_code == 200:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{filename_prefix}_{timestamp}.png"
                    filepath = GENERATED_DIR / filename
                    
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                        
                    print(f"✅ 이미지 저장 완료: {filepath}")
                    return str(filepath)
                else:
                    print(f"❌ 이미지 다운로드 실패: {response.status_code}")
            else:
                print("❌ 생성된 이미지가 없습니다.")
                
            return None

        except Exception as e:
            print(f"❌ 이미지 생성 중 오류 발생: {e}")
            # Mock Fallback (개발 중 API 오류 시에도 UI 흐름 확인용)
            return self._generate_mock_image(nanobanana_prompt, filename_prefix)

    def _generate_mock_image(self, prompt: str, filename_prefix: str) -> str:
        """API 실패 시 사용할 Mock 이미지 생성기."""
        try:
            from PIL import Image, ImageDraw
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_mock_{timestamp}.png"
            filepath = GENERATED_DIR / filename
            
            img = Image.new('RGB', (1024, 768), color = (30, 33, 40))
            d = ImageDraw.Draw(img)
            d.text((50,50), f"NanoBanana Mock Image\n{prompt[:100]}...", fill=(0, 255, 200))
            
            img.save(filepath)
            return str(filepath)
        except Exception:
            return None

# 싱글톤
image_gen = ImageGenerator()
