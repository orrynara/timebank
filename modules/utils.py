"""유틸리티 모듈.

이미지 로딩 등 공통적으로 사용되는 헬퍼 함수들을 제공합니다.
"""

import os
import streamlit as st
from PIL import Image, UnidentifiedImageError, ImageDraw

def load_image_safe(path: str, fallback_path: str = "assets/img/caravan_main.jpg") -> Image.Image:
    """
    이미지를 안전하게 로드합니다.
    파일이 없거나, 0byte이거나, 손상된 경우에도 절대 에러를 내지 않고
    회색 Placeholder 이미지를 반환합니다.

    Args:
        path (str): 로드할 이미지 경로
        fallback_path (str): 실패 시 대체할 기본 이미지 경로 (이것조차 실패하면 회색 박스 반환)

    Returns:
        PIL.Image.Image: 로드된 이미지 객체 (또는 대체 이미지)
    """
    try:
        # 1. 파일 존재 여부 확인
        if not os.path.exists(path):
            # st.warning(f"파일을 찾을 수 없음: {path}") # UI 공해 방지를 위해 로그는 생략하거나 debug 모드에서만
            return _load_fallback(fallback_path)

        # 2. 파일 크기 확인 (0KB 체크)
        if os.path.getsize(path) == 0:
            st.warning(f"⚠️ 손상된 파일(0byte)이 감지됨: {path}")
            return _load_fallback(fallback_path)

        # 3. 이미지 열기 시도
        image = Image.open(path)
        image.load()  # 실제 비트맵 데이터 로딩 (여기서 깨진 파일 걸러짐)
        return image

    except (UnidentifiedImageError, OSError, IOError) as e:
        st.error(f"❌ 이미지 로딩 실패 ({os.path.basename(path)}): {e}")
        return _load_fallback(fallback_path)
    except Exception as e:
        st.error(f"❌ 알 수 없는 오류 ({os.path.basename(path)}): {e}")
        return _load_fallback(fallback_path)

def _load_fallback(path: str) -> Image.Image:
    """
    Fallback 이미지 로드를 시도하고, 그것마저 실패하면
    회색 Placeholder 이미지를 생성하여 반환합니다.
    """
    try:
        # Fallback 경로 유효성 체크
        if path and os.path.exists(path) and os.path.getsize(path) > 0:
            return Image.open(path)
    except Exception:
        pass  # Fallback 로딩 실패는 조용히 무시하고 회색 박스 생성

    return create_placeholder_image()

def create_placeholder_image(width: int = 400, height: int = 300, text: str = "No Image") -> Image.Image:
    """
    회색 배경의 Placeholder 이미지를 생성합니다.
    """
    img = Image.new('RGB', (width, height), color=(200, 200, 200))
    # 텍스트를 그릴 수 있으면 좋겠지만, 폰트 의존성 없이 단순 색상만 반환해도 충분함
    # 필요하다면 ImageDraw를 사용하여 X 표시 등을 그릴 수 있음
    draw = ImageDraw.Draw(img)
    draw.line((0, 0) + img.size, fill=(150, 150, 150), width=3)
    draw.line((0, img.size[1], img.size[0], 0), fill=(150, 150, 150), width=3)
    return img
