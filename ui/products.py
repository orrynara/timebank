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
    tab_model_a, tab_model_b, tab_catalog = st.tabs(["SC-56-S (2인형)", "SC-85-V (4인형 패밀리)", "📚 카탈로그"])

    # --- 1. SC-56-S (2인형) ---
    with tab_model_a:
        st.subheader("SC-56-S: 커플을 위한 프라이빗 캡슐")
        
        # 탭 분리: 외관 / 상세 스펙 / 내부
        subtab_ext, subtab_spec, subtab_int = st.tabs(["외관 (Exterior)", "상세 스펙 (Specs)", "내부 (Interior)"])
        
        with subtab_ext:
            # 외관 이미지
            img_path = os.path.join("assets", "products", "0. 캡슐 카라반 모든 상품소개서 (종합)", "0. SC-56-S img_3.jpg")
            if os.path.exists(img_path):
                st.image(img_path, caption="SC-56-S Exterior Design", width="stretch")
            else:
                st.info("외관 이미지 준비 중입니다.")
                
        with subtab_spec:
            # 스펙 이미지 (이미지로 된 상세 내역)
            spec_img_path = os.path.join("assets", "products", "0. 캡슐 카라반 모든 상품소개서 (종합)", "0.SC-56-S spec 캡슐 카라반 상품소개서 (종합)_2.jpg")
            if os.path.exists(spec_img_path):
                 st.image(spec_img_path, caption="SC-56-S Technical Specifications", width="stretch")
            else:
                st.info("스펙 상세 이미지 준비 중입니다.")

        with subtab_int:
            st.markdown("##### 🛋️ 미래지향적 인테리어")
            # 내부 이미지 갤러리 (01. 폴더 + img 폴더)
            
            # 1. 01. 폴더 이미지
            int_dir = os.path.join("assets", "products", "01. 상품안내서 (우주선 5.6 형)2025")
            int_images = []
            if os.path.exists(int_dir):
                int_images = [os.path.join(int_dir, f) for f in os.listdir(int_dir) if f.lower().endswith(('.jpg', '.png'))]
            
            # 2. img 폴더 추가 이미지 (예시)
            extra_img_dir = "img"
            if os.path.exists(extra_img_dir):
                 # 특정 키워드가 있거나, 그냥 예시로 몇 개 가져옴
                 extra_images = [os.path.join(extra_img_dir, f) for f in os.listdir(extra_img_dir) if "caravan" in f.lower() or "interior" in f.lower()]
                 # int_images.extend(extra_images) # 필요시 활성화

            if int_images:
                # 2열 그리드
                cols = st.columns(2)
                for idx, img_p in enumerate(int_images):
                     with cols[idx % 2]:
                         st.image(img_p, width="stretch", caption=os.path.basename(img_p))
            else:
                st.info("내부 이미지가 준비되지 않았습니다.")

        st.divider()
        st.button("SC-56-S 상담 신청", key="btn_sc56", type="primary")

    # --- 2. SC-85-V (4인형 패밀리) ---
    with tab_model_b:
        st.subheader("SC-85-V: 온 가족을 위한 럭셔리 스테이션")
        
        subtab_ext, subtab_spec, subtab_int = st.tabs(["외관 (Exterior)", "상세 스펙 (Specs)", "내부 (Interior)"])
        
        with subtab_ext:
            img_path = os.path.join("assets", "products", "0. 캡슐 카라반 모든 상품소개서 (종합)", "0. SC-85-V img.jpg")
            if os.path.exists(img_path):
                st.image(img_path, caption="SC-85-V Exterior Design", width="stretch")
            else:
                st.info("외관 이미지 준비 중입니다.")
                
        with subtab_spec:
            spec_img_path = os.path.join("assets", "products", "0. 캡슐 카라반 모든 상품소개서 (종합)", "0. SC-85-V spec 캡슐 카라반 상품소개서 (종합)_4.jpg")
            if os.path.exists(spec_img_path):
                st.image(spec_img_path, caption="SC-85-V Technical Specifications", width="stretch")
            else:
                st.info("스펙 상세 이미지 준비 중입니다.")

        with subtab_int:
            st.markdown("##### 🛋️ 프리미엄 패밀리 인테리어")
            
            int_dir = os.path.join("assets", "products", "02. 상품안내서 (우주선 8.5 형)2025년")
            int_images = []
            if os.path.exists(int_dir):
                int_images = [os.path.join(int_dir, f) for f in os.listdir(int_dir) if f.lower().endswith(('.jpg', '.png'))]
            
            if int_images:
                cols = st.columns(2)
                for idx, img_p in enumerate(int_images):
                     with cols[idx % 2]:
                         st.image(img_p, width="stretch", caption=os.path.basename(img_p))
            else:
                st.info("내부 이미지가 준비되지 않았습니다.")

        st.divider()
        st.button("SC-85-V 상담 신청", key="btn_sc85", type="primary")

    # --- 3. 카탈로그 ---
    with tab_catalog:
        st.subheader("📄 공식 카탈로그 다운로드")
        
        # assets/products 폴더의 PDF 파일 나열
        products_dir = os.path.join("assets", "products")
        if os.path.exists(products_dir):
            pdf_files = [f for f in os.listdir(products_dir) if f.lower().endswith('.pdf')]
            for pdf in pdf_files:
                file_path = os.path.join(products_dir, pdf)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"📥 {pdf}",
                        data=f,
                        file_name=pdf,
                        mime="application/pdf"
                    )
        else:
            st.write("등록된 카탈로그가 없습니다.")
