"""테스트: AI 배경 이미지 생성.
modules/image_manager.py를 사용하여 이미지를 생성하고 저장하는지 확인합니다.
"""
import os
import sys
from pathlib import Path

# Windows 콘솔 인코딩 문제 해결
sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from modules.image_manager import image_gen

def test_generate_background():
    print("🚀 배경 이미지 생성 테스트 시작...")
    
    prompt = "Futuristic glamping site in Yangpyeong mountains, river view, peaceful nature, sci-fi caravan, autumn vibes"
    region_id = "test_yangpyeong"
    
    # 이미지 생성 요청
    result_path = image_gen.generate_image(prompt, region_id)
    
    if result_path and os.path.exists(result_path):
        print(f"✅ 성공: 이미지가 생성되었습니다. -> {result_path}")
    else:
        print("❌ 실패: 이미지 생성에 실패했습니다.")

if __name__ == "__main__":
    test_generate_background()
