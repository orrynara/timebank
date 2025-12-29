"""TimeBank 메인 홈 UI.

- Streamlit 화면 렌더링을 담당합니다.
- 비즈니스 로직은 modules/ 패키지에서 가져옵니다.
"""

import streamlit as st
import os
import datetime
from modules.utils import load_image_safe
from modules.core_logic import get_system

# UI 컴포넌트 로드
from ui.booking import render_booking_page
from ui.products import render_products_page
from ui.investor import render_investor_page
from ui.admin import render_admin_page
from ui.studio import render_studio_page 

def main() -> None:
    """메인 실행 함수.
    
    모든 UI 렌더링 로직의 최상위 진입점입니다.
    """
    
    # --- 페이지 설정 ---
    st.set_page_config(
        page_title="TimeBank: 미래형 카라반 공유 플랫폼",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"  # 사이드바 기본 접음 (Hero 섹션 강조)
    )

    # --- CSS 스타일 커스터마이징 (Airbnb Style & Global) ---
    st.markdown("""
    <style>
        /* 메인 헤더 스타일 */
        .main-header {
            font-size: 3rem;
            font-weight: 800;
            color: #FFFFFF;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin-bottom: 0.5rem;
        }
        
        /* 탭 스타일 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
            padding-bottom: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f7f7f7;
            border-radius: 25px; /* 둥근 탭 */
            padding-left: 25px;
            padding-right: 25px;
            color: #333;
            border: 1px solid #ddd;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FF385C; /* Airbnb Red */
            color: white;
            border: none;
        }

        /* 검색 바 컨테이너 스타일 */
        .search-container {
            background-color: white;
            padding: 10px 30px;
            border-radius: 40px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
            margin: -40px auto 30px auto; /* 비디오 위로 겹치게, 중앙 정렬 */
            max-width: 900px;
            position: relative;
            z-index: 100;
            border: 1px solid #ebebeb;
            display: flex;
            align-items: center;
        }
        
        /* 검색 내부 레이블 스타일 */
        .search-label {
            font-size: 0.8rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 2px;
        }
        .search-sub {
            font-size: 0.85rem;
            color: #717171;
        }
        
        /* 버튼 스타일 */
        div.stButton > button {
            border-radius: 20px;
            font-weight: bold;
        }
        
        /* Hero Section Video/Image Container */
        .hero-container {
            width: 100%;
            height: 500px;
            overflow: hidden;
            border-radius: 0 0 20px 20px;
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # --- 사이드바 ---
    with st.sidebar:
        # 로고 적용
        logo_path = os.path.join("assets", "TIMEBANK LOGO1 .png")
        logo_img = load_image_safe(logo_path)
        st.image(logo_img, width=200) # use_container_width=True -> width로 변경 권장됨
            
        st.header("TimeBank Menu")
        st.info("로그인 상태: 비회원 (체험 모드)")
        
        # 메뉴 네비게이션
        menu_selection = st.radio(
            "메뉴 이동",
            ["홈 (Home)", "상품 소개", "예약하기", "투자 정보", "크리에이티브 스튜디오", "관리자"]
        )
        
        st.markdown("---")
        st.caption("🚀 Version 1.3.1 (Hero Video Updated)")

    # --- 메인 컨텐츠 영역 ---
    
    # 홈 화면일 때만 Hero Section 표시
    if menu_selection == "홈 (Home)":
        
        # 1. Hero Section (Video Background)
        # 사용자 요청: assets/img/hero_video.mp4 사용
        hero_video_path = os.path.join("assets", "img", "hero_video.mp4")
        
        # 비디오/이미지를 꽉 차게 보여주기
        if os.path.exists(hero_video_path):
             # Streamlit Video 플레이어
             st.video(hero_video_path, autoplay=True, loop=True, muted=True) 
        else:
            # 영상이 없으면 에러 메시지를 표시하여 디버깅을 돕거나, 기존 이미지로 대체
            # 사용자 피드백 반영: 영상이 안 뜨는 경우를 방지하기 위해 경로 확인 로그 대신 바로 대체 이미지 로직은 유지하되,
            # 만약 파일이 있는데 안 뜨는 것이라면 코덱 문제일 수 있음. 여기서는 파일 존재 여부만 체크.
            
            # fallback: carvan_main.jpg
            main_img_path = os.path.join("assets", "img", "caravan_main.jpg") 
            main_img = load_image_safe(main_img_path)
            st.image(main_img, use_container_width=True)
            
            # (디버깅용) 파일이 없어서 이미지가 뜬다면 사용자에게 알림 (개발 모드에서만 유효하겠지만)
            # st.warning(f"Hero video not found at: {hero_video_path}")

        # 2. Search Bar (Airbnb Style)
        # st.columns를 사용하여 검색 바 구현
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        # Streamlit 레이아웃 트릭: 컨테이너 내부 컬럼 사용
        # 검색바 모양: [ 여행지 | 체크인 날짜 | 여행자 | 검색버튼 ]
        
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown('<p class="search-label">여행지</p>', unsafe_allow_html=True)
                # Selectbox 라벨을 숨기고 커스텀 레이아웃
                system = get_system()
                region_names = ["지도 전체"] + [r.name for r in system.get_regions()]
                st.selectbox("여행지 선택", region_names, label_visibility="collapsed")
            
            with col2:
                st.markdown('<p class="search-label">날짜</p>', unsafe_allow_html=True)
                st.date_input("체크인", datetime.date.today(), label_visibility="collapsed")
            
            with col3:
                st.markdown('<p class="search-label">여행자</p>', unsafe_allow_html=True)
                st.number_input("인원수", min_value=1, value=2, label_visibility="collapsed")
                
            with col4:
                st.markdown('<p class="search-label">&nbsp;</p>', unsafe_allow_html=True) # 줄맞춤용 공백
                if st.button("🔍", type="primary", use_container_width=True):
                    st.toast("검색 결과가 업데이트되었습니다! (데모)")
                    st.session_state['menu_selection'] = "예약하기" # 예약 페이지로 이동 유도 (구현 복잡도상 토스트만)
                    
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # [마케팅 배너]
        st.info("📣 **[투지아 스마트] 멤버십 런칭!** 월 2만원에 평일 4시간 무료 이용 혜택을 놓치지 마세요!")

        st.markdown("### ✨ TimeBank 추천 여행지")

    # --- 라우팅 (메뉴 선택에 따른 화면 표시) ---
    
    if menu_selection == "홈 (Home)":
        # 홈 화면에서는 주요 기능 탭으로 보여주기
        # 탭 순서: 예약(메인) > 스튜디오 > 투자 > 상품
        tab1, tab2, tab3, tab4 = st.tabs(["🏕️ 탐험하기 (예약)", "🎨 크리에이티브 스튜디오", "💰 투자자 정보", "🛸 상품 소개"])
        with tab1:
            render_booking_page()
        with tab2:
            render_studio_page()
        with tab3:
            render_investor_page()
        with tab4:
            render_products_page()
            
    elif menu_selection == "상품 소개":
        render_products_page()
        
    elif menu_selection == "예약하기":
        render_booking_page()
        
    elif menu_selection == "투자 정보":
        render_investor_page()
    
    elif menu_selection == "크리에이티브 스튜디오":
        render_studio_page()
        
    elif menu_selection == "관리자":
        render_admin_page()

    # --- 하단 푸터 ---
    st.markdown("---")
    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
         st.caption("© 2025 TimeBank Inc. | 공간과 시간을 저축하세요.")
    with col_f2:
         st.caption("고객센터: 1544-0000 | 이용약관 | 개인정보처리방침")

if __name__ == "__main__":
    main()
