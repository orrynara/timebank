"""크리에이티브 스튜디오 UI 모듈.

사용자가 배경 이미지를 생성하거나, 기존 이미지를 활용해
살아있는 홍보 영상(Video)을 만들 수 있는 도구입니다.
"""

import streamlit as st
import os
import glob
from modules.image_generator import image_gen

def _get_generated_files():
    """assets/generated 폴더의 모든 미디어 파일(.png, .mp4)을 가져옵니다."""
    # 이미지와 동영상 모두 수집
    images = glob.glob(os.path.join("assets", "generated", "*.png"))
    videos = glob.glob(os.path.join("assets", "generated", "*.mp4"))
    all_files = images + videos
    
    # 최신순 정렬
    all_files.sort(key=os.path.getmtime, reverse=True)
    return all_files

def _get_generated_images():
    """assets/generated 폴더의 이미지 목록만 가져옵니다 (영상 생성 소스용)."""
    files = glob.glob(os.path.join("assets", "generated", "*.png"))
    files.sort(key=os.path.getmtime, reverse=True)
    return files

def render_studio_page():
    """스튜디오 탭 메인 화면."""
    st.header("🎨 크리에이티브 스튜디오")
    st.markdown("나만의 배경을 만들고, **살아있는 영상**으로 재탄생시키세요.")

    tab1, tab2 = st.tabs(["🖼️ 이미지 생성 (Image Gen)", "🎬 영상 제작 (Image to Video)"])

    # ----------------------------------------------------------------
    # 탭 1: 이미지 생성
    # ----------------------------------------------------------------
    with tab1:
        st.subheader("나만의 캠핑장 배경 만들기")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            prompt_input = st.text_area(
                "어떤 풍경을 원하시나요?", 
                placeholder="예: 눈 덮인 자작나무 숲, 반딧불이가 빛나는 밤하늘, 벚꽃이 만개한 호수...",
                height=100
            )
            
            if st.button("✨ 배경 이미지 생성하기", type="primary"):
                if not prompt_input:
                    st.warning("프롬프트를 입력해주세요.")
                else:
                    try:
                        with st.spinner("Gemini가 상상력을 발휘하는 중입니다... (약 10~20초)"):
                            # 'custom' 접두사 사용
                            new_path = image_gen.generate_image(prompt_input, "custom")
                            
                            if new_path:
                                st.success("이미지 생성 완료!")
                                st.image(new_path, caption="새로 생성된 배경", use_container_width=True)
                            else:
                                st.error("이미지 생성에 실패했습니다. (결과값 None)")
                                
                    except Exception as e:
                        # 429 에러(Quota Exceeded) 핸들링
                        error_str = str(e)
                        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                            st.error("⚠️ **API 사용량이 초과되었습니다.** (Google Gemini API Quota Exceeded)")
                            st.info("잠시 후(약 1분 뒤) 다시 시도해주세요. 무료 티어 사용 시 분당 요청 제한이 있을 수 있습니다.")
                        else:
                            st.error(f"에러 상세: {error_str}")
                            import traceback
                            st.text(traceback.format_exc())

        with col2:
            st.info("💡 **Tip**")
            st.markdown("""
            - 구체적일수록 좋습니다.
            - 계절, 시간대, 날씨를 포함해보세요.
            - 생성된 이미지는 '영상 제작' 탭에서 바로 사용할 수 있습니다.
            """)

    # ----------------------------------------------------------------
    # 탭 2: 영상 제작 (Veo 3.1)
    # ----------------------------------------------------------------
    with tab2:
        st.subheader("살아있는 홍보 영상 만들기 (Powered by Veo 3.1)")
        
        # 1. 이미지 선택
        st.markdown("#### 1. 원본 이미지 선택")
        
        # 업로드 vs 라이브러리 선택
        upload_option = st.radio("이미지 소스", ["기존 생성 이미지 선택", "새 파일 업로드"], horizontal=True)
        
        selected_image_path = None
        
        if upload_option == "기존 생성 이미지 선택":
            images = _get_generated_images()
            if not images:
                st.warning("생성된 이미지가 없습니다. 옆 탭에서 먼저 이미지를 생성해보세요!")
            else:
                img_options = {os.path.basename(p): p for p in images}
                selected_filename = st.selectbox("이미지를 선택하세요", list(img_options.keys()))
                
                if selected_filename:
                    selected_image_path = img_options[selected_filename]
                    st.image(selected_image_path, caption="선택된 이미지", width=400)
                    
        else: # 새 파일 업로드
            uploaded_file = st.file_uploader("이미지를 업로드하세요 (PNG, JPG)", type=["png", "jpg", "jpeg"])
            if uploaded_file:
                # 임시 저장
                temp_path = os.path.join("assets", "generated", f"upload_{uploaded_file.name}")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                selected_image_path = temp_path
                st.image(selected_image_path, caption="업로드된 이미지", width=400)

        # 2. 영상 프롬프트 입력
        if selected_image_path:
            st.markdown("#### 2. 영상 연출 지시")
            video_prompt = st.text_input(
                "카메라 움직임이나 변화를 설명해주세요",
                placeholder="예: 카메라가 천천히 줌인하면서 잎사귀가 흔들림, 드론이 상승하며 전경을 비춤..."
            )
            
            if st.button("🎬 영상 생성 시작 (Veo 3.1)", type="primary"):
                if not video_prompt:
                    st.warning("영상 연출 지시(프롬프트)를 입력해주세요.")
                else:
                    try:
                        with st.spinner("Veo가 영상을 렌더링 중입니다... (약 1분 소요)"):
                            video_path = image_gen.generate_video(selected_image_path, video_prompt)
                            
                            if video_path:
                                st.success("영상 생성이 완료되었습니다!")
                                st.video(video_path)
                                st.markdown(f"**저장 경로:** `{video_path}`")
                            else:
                                st.error("영상 생성 실패. 잠시 후 다시 시도하거나 로그를 확인하세요.")
                                
                    except Exception as e:
                         # 429 에러(Quota Exceeded) 핸들링
                        error_str = str(e)
                        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                            st.error("⚠️ **API 사용량이 초과되었습니다.** (Google Veo API Quota Exceeded)")
                            st.info("잠시 후(약 1분 뒤) 다시 시도해주세요. 무료 티어 사용 시 분당 요청 제한이 있을 수 있습니다.")
                        else:
                            st.error(f"에러 상세: {error_str}")
                            import traceback
                            st.text(traceback.format_exc())

    # ----------------------------------------------------------------
    # 공통: 갤러리 섹션 (하단)
    # ----------------------------------------------------------------
    st.markdown("---")
    st.subheader("📂 나의 창작물 갤러리")
    
    # 갤러리 새로고침 버튼 (파일 생성 후 즉시 반영이 안 될 때 유용)
    if st.button("🔄 갤러리 새로고침"):
        st.rerun()

    gallery_files = _get_generated_files()
    
    if not gallery_files:
        st.info("아직 생성된 창작물이 없습니다. 위에서 멋진 이미지나 영상을 만들어보세요!")
    else:
        # 3열 그리드로 표시
        cols = st.columns(3)
        for idx, file_path in enumerate(gallery_files):
            file_name = os.path.basename(file_path)
            ext = os.path.splitext(file_name)[1].lower()
            
            with cols[idx % 3]:
                # 컨테이너로 감싸서 깔끔하게
                with st.container(border=True):
                    if ext in ['.mp4', '.mov', '.avi']:
                        st.video(file_path)
                        st.caption(f"🎬 {file_name}")
                    elif ext in ['.png', '.jpg', '.jpeg', '.webp']:
                        st.image(file_path, use_container_width=True)
                        st.caption(f"🖼️ {file_name}")
                    else:
                        st.text(file_name)
