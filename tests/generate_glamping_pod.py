#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자 요청 프롬프트로 Z-Image Turbo 이미지 생성
"""

import os
import sys
import time
import replicate
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 사용자 요청 프롬프트
user_prompt = """
A hyper-realistic, close-up portrait of a tribal elder from the Omo Valley, painted with intricate white chalk patterns and adorned with a headdress made of dried flowers, seed pods, and rusted bottle caps. The focus is razor-sharp on the texture of the skin, showing every pore, wrinkle, and scar that tells a story of survival. The background is a blurred, smoky hut interior, with the warm glow of a cooking fire reflecting in the subject's dark, soulful eyes. Shot on a Leica M6 with Kodak Portra 400 film grain aesthetic.
"""

def generate_image():
    """
    사용자 프롬프트로 이미지 생성 및 저장 (다중 해상도 지원)
    """
    print("=" * 70)
    print("Z-Image Turbo 이미지 생성 요청")
    print("=" * 70)
    print()
    
    # 저장 경로 설정 (assets/generated)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_dir = os.path.join(base_dir, "assets", "generated")
    os.makedirs(save_dir, exist_ok=True)
    
    print(f"[OK] 저장 경로 확인: {save_dir}")
    print()
    
    # Replicate API 키 확인
    replicate_key = os.getenv("REPLICATE_API_TOKEN")
    if not replicate_key:
        print("[ERROR] REPLICATE_API_TOKEN이 설정되지 않았습니다.")
        return False
    
    print("[OK] Replicate API 키 확인 완료")
    print()
    
    # 프롬프트 출력
    print("[INFO] 프롬프트:")
    print("-" * 70)
    print(user_prompt.strip())
    print("-" * 70)
    print()
    
    # 해상도 목록 정의 (너비, 높이)
    # Z-Image Turbo 최대 해상도 제한: 1440px
    # 요청: 1920x1080 (16:9) -> 조정: 1440x800 (16:9 비율 유지 시도) -> 1440x816 (16배수)
    # 요청: 2048x2048 (1:1) -> 조정: 1024x1024 (1:1 권장)
    resolutions = [
        (1440, 816),   # 16:9 비율에 가까운 최대 해상도 (1920x1080 대응)
        (1024, 1024),  # 1:1 Square (2048x2048 대응)
    ]
    
    print(f"[INFO] 총 {len(resolutions)}개의 해상도로 이미지 생성을 시도합니다.")
    print()
    
    success_count = 0
    
    for width, height in resolutions:
        print(f"[INFO] 생성 시작: {width}x{height}...")
        start_time = time.time()
        
        try:
            # 해상도 16배수 보정
            adjusted_width = (width // 16) * 16
            adjusted_height = (height // 16) * 16
            
            if adjusted_width != width or adjusted_height != height:
                print(f"   [WARN] 16배수 보정: {width}x{height} -> {adjusted_width}x{adjusted_height}")
            
            output = replicate.run(
                "prunaai/z-image-turbo",
                input={
                    "prompt": user_prompt,
                    "width": adjusted_width,
                    "height": adjusted_height,
                    "num_inference_steps": 4,
                    "guidance_scale": 1.5
                }
            )
            
            elapsed_time = time.time() - start_time
            print(f"   [INFO] 소요 시간: {elapsed_time:.2f}초")
            
            if not output:
                print("   [ERROR] 생성 실패: 빈 응답")
                continue
                
            # Output 처리
            if isinstance(output, list):
                image_data = output[0]
            else:
                image_data = output
                
            # 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tribal_elder_{adjusted_width}x{adjusted_height}_{timestamp}.png"
            file_path = os.path.join(save_dir, filename)
            
            # 저장 로직
            if hasattr(image_data, 'read'):
                with open(file_path, "wb") as file:
                    file.write(image_data.read())
            elif isinstance(image_data, str) and image_data.startswith("http"):
                import requests
                response = requests.get(image_data, timeout=30)
                response.raise_for_status()
                with open(file_path, "wb") as file:
                    file.write(response.content)
            elif isinstance(image_data, bytes):
                with open(file_path, "wb") as file:
                    file.write(image_data)
            
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"   [OK] 저장 완료: {filename} ({file_size:,} bytes)")
                success_count += 1
            else:
                print("   [WARN] 파일 저장 실패")
                
        except Exception as e:
            print(f"   [ERROR] 오류 발생 ({width}x{height}): {str(e)}")
            
        print("-" * 30)

    print()
    print(f"[RESULT] 총 {len(resolutions)}개 중 {success_count}개 생성 성공")
    return success_count > 0

if __name__ == "__main__":
    success = generate_image()
    sys.exit(0 if success else 1)
