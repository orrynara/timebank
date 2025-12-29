#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Z-Image Turbo 모델 9:16 비율 검증 테스트
실제 시나리오 프롬프트를 사용하여 정상 작동 확인
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

# 실제 사용자 제공 프롬프트 (하이퍼 리얼리스틱 디테일 버전)
real_prompt = """
A hyper-realistic, candid style photograph of two young women backstage, bathed in dramatic, low-key lighting. A warm, dusty spotlight beam cuts through the darkness, highlighting the textures of their clothing and hair. On the left, a girl with dark hair in a loose, messy bun wears a worn white cotton T-shirt and light-colored pants; her expression shows nervous energy. Next to her, another girl in a cozy, chunky knit oversized beige sweater and round glasses looks on calmly, light reflecting slightly off her lenses. The background is a cluttered, atmospheric backstage area with tangled cables, flight cases, and dark velvet curtains, all rendered with a shallow depth of field and a film grain aesthetic. Shot on 35mm film.
"""

def test_custom_prompt_9_16():
    """
    실제 시나리오 프롬프트로 Z-Image Turbo 9:16 비율 테스트
    replicate 라이브러리 직접 사용
    """
    print("=" * 70)
    print("Z-Image Turbo 9:16 비율 테스트 (실제 프롬프트)")
    print("=" * 70)
    print()
    
    # testresult 폴더 생성 (없으면)
    result_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "testresult")
    os.makedirs(result_dir, exist_ok=True)
    print(f"✓ 결과 폴더 준비: {result_dir}")
    print()
    
    # Replicate API 키 확인
    replicate_key = os.getenv("REPLICATE_API_TOKEN")
    if not replicate_key:
        print("❌ REPLICATE_API_TOKEN이 설정되지 않았습니다.")
        print("   .env 파일에 REPLICATE_API_TOKEN을 추가하세요.")
        return False
    
    print("✓ Replicate API 키 확인 완료")
    print()
    
    # 테스트 프롬프트 출력
    print("📝 테스트 프롬프트:")
    print("-" * 70)
    print(real_prompt)
    print("-" * 70)
    print()
    
    # 테스트 파라미터
    print("🔧 테스트 설정:")
    print("   모델: prunaai/z-image-turbo")
    print("   해상도: 576x1024 (9:16 비율)")
    print("   Inference Steps: 4")
    print()
    
    # Replicate API 직접 호출
    print("🚀 이미지 생성 시작...")
    start_time = time.time()
    
    try:
        output = replicate.run(
            "prunaai/z-image-turbo",
            input={
                "prompt": real_prompt,
                "width": 576,
                "height": 1024,
                "num_inference_steps": 4,
                "guidance_scale": 1.5
            }
        )
        
        elapsed_time = time.time() - start_time
        print(f"⏱️  소요 시간: {elapsed_time:.2f}초")
        print()
        
        # 결과 확인
        if not output:
            print("❌ 생성 실패: 빈 응답")
            return False
        
        print("✅ 생성 성공!")
        
        # 결과 처리 및 저장
        print()
        print("📥 이미지 저장 중...")
        try:
            # output 형식 판단 및 처리
            if isinstance(output, list):
                image_data = output[0]
            else:
                image_data = output
            
            # 파일명 생성 (타임스탬프 포함)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(result_dir, f"z_turbo_result_{timestamp}.png")
            
            # 이미지 데이터 저장
            if hasattr(image_data, 'read'):
                # 파일 객체인 경우
                with open(file_path, "wb") as file:
                    file.write(image_data.read())
                    
            elif isinstance(image_data, str) and image_data.startswith("http"):
                # URL 문자열인 경우
                import requests
                response = requests.get(image_data, timeout=30)
                response.raise_for_status()
                with open(file_path, "wb") as file:
                    file.write(response.content)
                    
            elif isinstance(image_data, bytes):
                # 바이너리 데이터인 경우
                with open(file_path, "wb") as file:
                    file.write(image_data)
                    
            else:
                print(f"⚠️  예상치 못한 데이터 형식: {type(image_data)}")
                print(f"   데이터: {str(image_data)[:100]}")
                return False
            
            # 저장 확인
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"✅ Image saved to: {os.path.relpath(file_path)}")
                print(f"   파일 크기: {file_size:,} bytes")
            else:
                print(f"⚠️  파일 저장 확인 실패: {file_path}")
                return False
            
        except Exception as e:
            print(f"⚠️  이미지 저장 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print()
        print("=" * 70)
        print("테스트 성공: Z-Image Turbo가 9:16 비율로 정상 작동합니다.")
        print("=" * 70)
        return True
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"⏱️  소요 시간: {elapsed_time:.2f}초")
        print()
        print("❌ API 호출 실패")
        print(f"   에러: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 실행"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "Z-Image Turbo 검증 테스트" + " " * 28 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 테스트 1: 실제 프롬프트 테스트
    test1_result = test_custom_prompt_9_16()
    
    # 테스트 2: 직접 호출 테스트 (선택사항)
    # test2_result = test_z_image_direct()
    
    # 최종 결과
    print()
    print("=" * 70)
    print("최종 결과")
    print("=" * 70)
    print(f"실제 프롬프트 테스트: {'✅ 통과' if test1_result else '❌ 실패'}")
    # print(f"직접 호출 테스트: {'✅ 통과' if test2_result else '❌ 실패'}")
    print("=" * 70)
    print()
    
    return test1_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
