import os
import requests
import base64
import json

# API 설정
API_KEY = "448f6cafdea14139965c73782140c154"
BASE_URL = "https://api.aimlapi.com/v1/images/generations"

# 대상 이미지 파일
IMAGE_FILES = ["basic_model.png", "durico_test1.png"]
OUTPUT_DIR = "result"

# 프롬프트 설정
PROMPT = "The character from the original image cleaning inside a supermarket, holding a mop or cleaning tool, supermarket shelves in background, highly detailed, 8k, realistic texture"

# 모델 설정 (Nano Banana Pro)
# 에러 로그 분석 결과 -edit 접미사가 있는 모델이 존재함
MODEL = "google/nano-banana-pro-edit"

def encode_image_to_base64(image_path):
    """이미지 파일을 읽어 Base64 문자열로 변환"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
    # 확장자 확인
    ext = os.path.splitext(image_path)[1].lower().replace('.', '')
    if ext == 'jpg': ext = 'jpeg'
    
    return f"data:image/{ext};base64,{encoded_string}"

def generate_i2i(image_path, prompt, aspect_ratio):
    """Image-to-Image 생성 요청"""
    data_url = encode_image_to_base64(image_path)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Nano Banana Pro Edit 모델은 image_urls 배열을 요구할 가능성이 높음 (Seedream과 유사)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "image_urls": [data_url], 
        "aspect_ratio": aspect_ratio,
        "strength": 0.7, # 원본 유지 강도
        "n": 1
    }
    
    print(f"\n[생성 요청] 파일: {image_path}")
    print(f"모델: {MODEL}")
    print(f"비율: {aspect_ratio}")
    
    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 생성 실패: {e}")
        if response.content:
            print(f"응답 내용: {response.text}")
        return None

def save_image(url, filename):
    """URL에서 이미지를 다운로드하여 저장"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "wb") as f:
            f.write(response.content)
        print(f"✅ 저장 완료: {path}")
    except Exception as e:
        print(f"❌ 저장 실패: {e}")

def main():
    # 결과 폴더 생성
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # 테스트할 비율 목록 (세로, 가로)
    ratios = ["9:16", "16:9"]
    
    for img_file in IMAGE_FILES:
        if not os.path.exists(img_file):
            print(f"⚠️ 파일을 찾을 수 없습니다: {img_file}")
            continue
            
        for ratio in ratios:
            result = generate_i2i(img_file, PROMPT, ratio)
            
            if result and 'data' in result:
                for i, item in enumerate(result['data']):
                    url = item.get('url')
                    if url:
                        # 파일명 생성: 원본명_nanobanana_비율_번호.png
                        ratio_str = ratio.replace(":", "x")
                        base_name = os.path.splitext(img_file)[0]
                        save_name = f"{base_name}_nanobanana_{ratio_str}_{i+1}.png"
                        save_image(url, save_name)
            else:
                print(f"결과를 가져오지 못했습니다: {img_file} ({ratio})")

if __name__ == "__main__":
    main()
