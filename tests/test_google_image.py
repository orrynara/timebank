import os
import sys
import base64

# Windows 콘솔 인코딩 문제 해결
sys.stdout.reconfigure(encoding='utf-8')

import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

# 1. 환경 변수 로드
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Error: GOOGLE_API_KEY environment variable not found.")
    sys.exit(1)

# 2. Google AI 설정
genai.configure(api_key=api_key)

# 3. 테스트 설정
# 이미지 생성 시도 모델
target_gen_models = [
    'models/gemini-2.0-flash-exp-image-generation', 
    'models/gemini-3-pro-image-preview'
]
# 비전(분석) 대체 모델
vision_model_name = 'models/gemini-1.5-flash' 

prompt = "A futuristic eco-friendly camping pod in a Korean forest, photorealistic, 8k, cinematic lighting"
output_path = "assets/generated/google_test_image.png"
test_image_path = "assets/TIMEBANK LOGO1 .png"

print(f"🚀 Starting Google AI Test...")

# 4. 이미지 생성 시도
image_generated = False
print("\n--- Phase 1: Image Generation Test ---")

for model_name in target_gen_models:
    print(f"Attempting with model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        # 이미지 생성을 위한 프롬프트 전송
        response = model.generate_content(prompt)
        
        # 응답 구조 확인 및 이미지 추출 시도
        # Gemini 모델이 이미지를 반환할 때 parts 내 inline_data로 올 가능성 체크
        if hasattr(response, 'parts'):
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    print("  > Image data found in response!")
                    img_data = base64.b64decode(part.inline_data.data)
                    
                    # 디렉토리 확인
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    with open(output_path, 'wb') as f:
                        f.write(img_data)
                    print(f"✅ Image saved to: {output_path}")
                    image_generated = True
                    break
        
        if not image_generated:
            print(f"  > No image data in response from {model_name}. Response might be text-only.")
            # 텍스트 응답이라도 출력해봄
            if hasattr(response, 'text'):
                print(f"  > Text response: {response.text[:100]}...")
            
    except Exception as e:
        print(f"  > Failed: {e}")
    
    if image_generated:
        break

# 5. 실패 시 Gemini Vision 테스트로 대체
if not image_generated:
    print("\n⚠️ Image Generation failed or returned no images.")
    print("--- Phase 2: Fallback to Gemini Vision (Image Analysis) ---")
    
    if os.path.exists(test_image_path):
        try:
            print(f"Analyzing image: {test_image_path}")
            model = genai.GenerativeModel(vision_model_name)
            img = Image.open(test_image_path)
            
            vision_prompt = "Describe this logo in detail and identify any text."
            response = model.generate_content([vision_prompt, img])
            
            print(f"✅ Vision Analysis Result:\n{response.text}")
            
        except Exception as e:
            print(f"❌ Vision Test Error: {e}")
            # 사용 가능한 모델 다시 확인
            print("\nCheck available models manually if 404 occurs.")
    else:
        print(f"❌ Test image for vision fallback not found: {test_image_path}")
else:
    print("\n🎉 Image Generation Successful!")

