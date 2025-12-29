import os
import sys
from io import BytesIO

from dotenv import load_dotenv
from PIL import Image

from google import genai
from google.genai.types import GenerateContentConfig, Modality


OUTPUT_DIR = r"D:\coding 2025\timebank\assets\generated"
PROMPT = "롯데월드에서 솜사탕을 들고 있는 kpop 여자 아이돌, 16:9, 고해상도, 자연스러운 조명, 사진 스타일"


def _extract_first_inline_image_bytes(response):
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


def generate_and_save_image(client: genai.Client, model_id: str, filename: str) -> str:
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[PROMPT],
            config=GenerateContentConfig(response_modalities=[Modality.IMAGE]),
        )

        image_bytes = _extract_first_inline_image_bytes(response)

        img = Image.open(BytesIO(image_bytes))
        full_path = os.path.join(OUTPUT_DIR, filename)
        img.save(full_path, format="PNG")
        return full_path

    except Exception as e:
        print(f"[ERROR] model={model_id} filename={filename} -> {e}")
        raise


if __name__ == "__main__":
    try:
        load_dotenv()

        gemini_key = os.getenv("GEMINI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")

        if not gemini_key:
            if google_key:
                print("[WARN] GEMINI_API_KEY not found; using GOOGLE_API_KEY instead.")
                gemini_key = google_key
            else:
                print("[ERROR] GEMINI_API_KEY is not set in .env (and GOOGLE_API_KEY is also missing).")
                sys.exit(1)

        client = genai.Client(api_key=gemini_key)

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        p1 = generate_and_save_image(
            client,
            model_id="gemini-3-pro-image-preview",
            filename="nanobanana_pro_lotteworld.png",
        )
        print("saved:", p1)

        p2 = generate_and_save_image(
            client,
            model_id="gemini-2.5-flash-image",
            filename="flash_image_lotteworld.png",
        )
        print("saved:", p2)

    except SystemExit:
        raise
    except Exception as e:
        print(f"[FATAL] {e}")
        sys.exit(1)
