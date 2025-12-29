"""TimeBank 상품 소개 페이지 모듈.

카라반 모델별 상세 정보와 카탈로그를 보여줍니다.
"""

import streamlit as st
import os

def render_products_page():
    """상품 소개 탭 화면 렌더링."""
    st.header("🛸 TimeBank 우주선 카라반 라인업")
    st.markdown("당신의 여행을 미래로 이끄는 혁신적인 모빌리티를 소개합니다.")

    # 탭으로 모델 구분
    tab_model_a, tab_model_b, tab_catalog = st.tabs(["Z5 우주선 (2인형)", "Z7 패밀리 (4인형)", "📚 카탈로그"])

    with tab_model_a:
        st.subheader("Z5: 커플을 위한 프라이빗 캡슐")
        col1, col2 = st.columns([1, 1])
        with col1:
            # 이미지 경로 확인 후 표시 (없으면 패스)
            img_path = os.path.join("assets", "products", "01. 상품안내서 (우주선 5.6 형)2025", "상품안내서 (우주선 5.6 형)2025_1.jpg")
            if os.path.exists(img_path):
                st.image(img_path, caption="Z5 Exterior", use_container_width=True)
            else:
                st.info("이미지 준비 중입니다.")
        with col2:
            st.markdown("""
            ### 주요 스펙
            - **크기**: 5.6m x 2.4m
            - **수용 인원**: 2인 (최대 3인)
            - **특징**: 
                - 360도 파노라마 윈도우
                - 음성 인식 AI 컨시어지
                - 초고속 스타링크 위성 인터넷
            """)
            st.button("Z5 상세 견적 보기", key="btn_z5")

    with tab_model_b:
        st.subheader("Z7: 온 가족을 위한 럭셔리 스테이션")
        col1, col2 = st.columns([1, 1])
        with col1:
            img_path = os.path.join("assets", "products", "02. 상품안내서 (우주선 8.5 형)2025년", "상품안내서 (우주선 8.5 형)2025년_1.jpg")
            if os.path.exists(img_path):
                st.image(img_path, caption="Z7 Exterior", use_container_width=True)
            else:
                st.info("이미지 준비 중입니다.")
        with col2:
            st.markdown("""
            ### 주요 스펙
            - **크기**: 8.5m x 3.0m
            - **수용 인원**: 4인 (최대 6인)
            - **특징**:
                - 확장형 거실 모듈
                - 듀얼 욕실 시스템
                - 스마트 팜 키친 탑재
            """)
            st.button("Z7 상세 견적 보기", key="btn_z7")

    with tab_catalog:
        st.subheader("📄 공식 카탈로그 다운로드")
        
        # assets/products 폴더의 PDF 파일 나열
        products_dir = os.path.join("assets", "products")
        if os.path.exists(products_dir):
            pdf_files = [f for f in os.listdir(products_dir) if f.lower().endswith('.pdf')]
            for pdf in pdf_files:
                file_path = os.path.join(products_dir, pdf)
                with open(file_path, "rb") as f:
                    btn = st.download_button(
                        label=f"📥 {pdf}",
                        data=f,
                        file_name=pdf,
                        mime="application/pdf"
                    )
        else:
            st.write("등록된 카탈로그가 없습니다.")
