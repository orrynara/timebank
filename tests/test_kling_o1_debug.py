"""
Kling Image O1 전용 디버깅 스크립트
- 수정 사항: image_url(문자열) 대신 image_urls(리스트) 강제 사용
"""
import requests
import json
import os
import base64
from PIL import Image

# ==========================================
# ✅ 설정 영역
# ==========================================
API_KEY = "448f6cafdea14139965c73782140c154"
TEST_DIR = r"D:\coding 2025\CanvasToon_Builder\test_character"

CHAR_FILES = ["DURICO HOME.png", "KIN_KONG.png", "MONKEY.png"]

# Kling은 묘사력과 스타일 반영이 중요하므로 프롬프트 디테일 유지
PROMPT = (
    "A cinematic shot of 3 characters camping at night. "
    "(Left) Yellow round mascot, durian-shaped spikes, vinyl toy texture, blue helmet. "
    "(Center) Large gorilla in silver armor. "
    "(Right) Cute brown monkey in red hoodie. "
    "They set up tents near campfire under starry sky. 8k, detailed plastic texture, 3d render style."
)

MODEL_ID = "klingai/image-o1"

# ==========================================
# 🛠️ 헬퍼 함수
# ==========================================
def encode_image(folder, filename=None, full_path=None):
    path = full_path if full_path else os.path.join(folder, filename)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"


def create_collage(image_paths, output_path):
    images = []
    print("🎨 콜라주 생성 중...")
    for path in image_paths:
        full_path = os.path.join(TEST_DIR, path)
        if os.path.exists(full_path):
            try:
                img = Image.open(full_path).convert("RGBA")
                base_height = 1024
                h_percent = base_height / float(img.size[1])
                w_size = int(float(img.size[0]) * h_percent)
                img = img.resize((w_size, base_height), Image.Resampling.LANCZOS)
                images.append(img)
            except Exception as e:
                print(f"⚠️ 이미지 처리 실패 ({path}): {e}")
    if not images:
        return None

    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)
    collage = Image.new('RGB', (total_width, max_height), (10, 10, 20))
    x_offset = 0
    for img in images:
        collage.paste(img, (x_offset, 0), img if img.mode == 'RGBA' else None)
        x_offset += img.width
    collage.save(output_path)
    return output_path


def call_api(payload, label, save_name):
    url = "https://api.aimlapi.com/v1/images/generations"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    print(f"\n📡 [{label}] 전송 중... ({payload['model']})")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)

        if response.status_code not in [200, 201]:
            print(f"❌ 실패 (Status: {response.status_code}): {response.text[:300]}...")
            return

        result = response.json()
        image_url = None
        if 'output' in result:
            image_url = result['output']['choices'][0]['image_url']
        elif 'data' in result:
            image_url = result['data'][0]['url']

        if image_url:
            print(f"✨ 성공! URL: {image_url}")
            save_path = os.path.join(TEST_DIR, save_name)
            with open(save_path, 'wb') as f:
                f.write(requests.get(image_url).content)
            print(f"💾 저장 완료: {save_name}")
        else:
            print(f"⚠️ URL 없음: {json.dumps(result, indent=2)}")

    except Exception as e:
        print(f"⚠️ 에러: {e}")


# ==========================================
# 🚀 메인 실행
# ==========================================
def run_test():
    print("🚀 Kling O1 Payload Fix 테스트 시작...")

    # 이미지 준비
    b64_list = []
    for fname in CHAR_FILES:
        encoded = encode_image(TEST_DIR, fname)
        if encoded:
            b64_list.append(encoded)
    
    collage_path = os.path.join(TEST_DIR, "temp_collage_final.png")
    if not os.path.exists(collage_path):
        create_collage(CHAR_FILES, collage_path)
    b64_collage = encode_image(None, full_path=collage_path)

    if not b64_list or not b64_collage:
        print("이미지 준비 실패")
        return

    # ▶️ TEST 1: Kling Multi-Source (3장 개별 전송)
    # Kling 문서: 최대 10장 지원. 가장 기대되는 모드.
    print("\n" + "=" * 50)
    payload_1 = {
        "model": MODEL_ID,
        "prompt": PROMPT,
        "image_urls": b64_list,  # [핵심] 리스트 그대로 전송
        "n": 1,
    }
    call_api(payload_1, "Kling Native Multi", "result_kling_native.png")

    # ▶️ TEST 2: Kling Collage Fix (1장 콜라주 전송)
    # [수정 포인트] 단일 이미지라도 image_urls 리스트에 넣어야 함!
    print("\n" + "=" * 50)
    payload_2 = {
        "model": MODEL_ID,
        "prompt": PROMPT,
        "image_urls": [b64_collage],  # [핵심] 리스트로 감싸서 전송! ([img])
        "n": 1,
    }
    call_api(payload_2, "Kling Collage Fix", "result_kling_collage_fixed.png")


if __name__ == "__main__":
    run_test()
