"""TimeBank 예약 페이지 모듈.

지역 및 캠핑장 선택, 날짜 지정, 결제 기능을 제공합니다.
Airbnb 스타일의 카드 그리드 UI를 채택하여 시각적 경험을 강화했습니다.
"""

import streamlit as st
import datetime
import os
import glob
from modules.core_logic import get_system
from modules.image_generator import image_gen
from modules.utils import load_image_safe

system = get_system()

def _load_latest_image(region_id):
    """해당 지역의 가장 최신 생성 이미지를 로드합니다."""
    search_pattern = os.path.join("assets", "generated", f"{region_id}_*.png")
    files = glob.glob(search_pattern)
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]

def render_booking_page():
    """예약하기 탭 화면 (Airbnb Style Grid)."""
    
    # 상단 헤더 삭제 (Home에서 탭으로 처리하거나 깔끔하게 유지)
    # st.header("🏕️ 탐험하기") 
    
    # 1. 데이터 가져오기 (Campsite 기준)
    # 기존 Region 기준이 아닌 Campsite 기준으로 변경하여 개별 상품 노출
    campsites = system.get_all_campsites()
    
    # --- 스타일: 카드 호버 효과 및 레이아웃 ---
    st.markdown("""
    <style>
        /* 카드 컨테이너 */
        .card-container {
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 0;
            margin-bottom: 20px;
            transition: box-shadow 0.3s ease;
            background-color: white;
            overflow: hidden; /* 이미지가 둥근 모서리 넘치지 않게 */
        }
        .card-container:hover {
            box-shadow: 0 6px 16px rgba(0,0,0,0.12);
        }
        
        /* 텍스트 영역 */
        .card-content {
            padding: 15px;
        }
        
        /* 타이틀 */
        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 4px;
            color: #222;
        }
        
        /* 부가 설명 */
        .card-desc {
            font-size: 0.9rem;
            color: #717171;
            margin-bottom: 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* 가격 및 평점 행 */
        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
        }
        
        .price-text {
            font-weight: 700;
            color: #222;
            font-size: 1rem;
        }
        
        .rating-box {
            display: flex;
            align-items: center;
            font-size: 0.9rem;
        }
        
        /* 예약 버튼 오버라이드 (카드 내부 버튼처럼 보이게) */
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

    # 2. 그리드 레이아웃 생성 (3열)
    # st.columns(3)을 루프 밖에서 선언하고 인덱스로 접근하는 방식은 데이터 개수가 많을 때 복잡함.
    # 행(row) 단위로 루프를 돌며 컬럼을 생성하는 방식 사용.
    
    cols_per_row = 3
    rows = [campsites[i:i + cols_per_row] for i in range(0, len(campsites), cols_per_row)]

    for row_items in rows:
        cols = st.columns(cols_per_row)
        for idx, campsite in enumerate(row_items):
            with cols[idx]:
                # --- 카드 UI 시작 ---
                
                # 1) 이미지 처리
                # campsite.images[0]가 있으면 사용, 없으면 fallback
                img_path = None
                if campsite.images:
                    img_path = campsite.images[0]
                
                # 이미지 로드 (URL이면 st.image가 알아서 처리, 로컬이면 load_image_safe)
                if img_path and img_path.startswith("http"):
                    st.image(img_path, use_container_width=True) # URL 직접 사용
                else:
                    # 로컬 파일 체크
                    if img_path and os.path.exists(img_path):
                        st.image(load_image_safe(img_path), use_container_width=True)
                    else:
                        # Fallback: 지역별 생성 이미지 또는 기본 이미지
                        latest = _load_latest_image(campsite.region_id)
                        if latest:
                            st.image(load_image_safe(latest), use_container_width=True)
                        else:
                            st.image(load_image_safe("assets/img/caravan_main.jpg"), use_container_width=True)

                # 2) 텍스트 정보
                st.markdown(f"<div class='card-title'>{campsite.name}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-desc'>{campsite.location_desc}</div>", unsafe_allow_html=True)
                
                # 3) 가격 및 평점
                st.markdown(f"""
                <div class='card-footer'>
                    <div class='price-text'>₩{campsite.base_price_weekday:,} <span style='font-weight:400; font-size:0.9em'>/ 시간</span></div>
                    <div class='rating-box'>★ {campsite.rating} ({campsite.review_count})</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 4) 예약하기 버튼
                # 버튼 키(key)를 유니크하게 설정해야 함
                if st.button("예약하기", key=f"btn_reserve_{campsite.id}"):
                    st.session_state.selected_campsite_id = campsite.id
                    st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True) # 간격
                
    # 3. 상세 예약 페이지 (Expander로 하단에 열림)
    if "selected_campsite_id" in st.session_state:
        target_id = st.session_state.selected_campsite_id
        # 해당 ID의 객체 찾기
        target_campsite = next((c for c in campsites if c.id == target_id), None)
        
        if target_campsite:
            st.markdown("---")
            with st.container():
                st.subheader(f"📝 예약 진행: {target_campsite.name}")
                
                c1, c2 = st.columns([1, 1])
                
                with c1:
                    # 날짜 선택
                    date = st.date_input("날짜 선택", min_value=datetime.date.today())
                    
                    # 시간 선택
                    time_options = {
                        "AM": "🌞 오전 Time (10:00 ~ 14:00) - 4시간",
                        "PM": "🌅 오후 Time (15:00 ~ 19:00) - 4시간",
                        "OVERNIGHT": "🌙 1박 2일 (15:00 ~ 11:00) - 숙박"
                    }
                    selected_time_key = st.radio(
                        "이용 시간",
                        list(time_options.keys()),
                        format_func=lambda x: time_options[x]
                    )

                with c2:
                    # 회원 구분
                    user_type = st.radio(
                        "회원 구분",
                        ["일반 회원 (비회원)", "타임뱅크 멤버십 회원"],
                        horizontal=True
                    )
                    is_member = (user_type == "타임뱅크 멤버십 회원")
                    
                    membership_type = "NONE"
                    if is_member:
                        membership_type = st.selectbox("보유 멤버십", ["M_SMART (투지아 스마트)", "M_ROYAL (리조트 로얄)"]).split(" ")[0]

                    # 가격 계산
                    is_weekend = (date.weekday() >= 5)
                    price = system.calculate_price(
                        target_campsite, 
                        is_member, 
                        membership_type, 
                        selected_time_key, 
                        is_weekend
                    )
                    
                    # 결제 정보 표시
                    st.success(f"**총 결제 금액: {price:,}원**")
                    if price == 0:
                        st.caption("✨ 멤버십 혜택이 적용되었습니다!")
                        
                    if st.button("결제 및 예약 확정", type="primary", use_container_width=True):
                         booking = system.create_booking(
                            user_id="current_user",
                            campsite_id=target_campsite.id,
                            date=date,
                            time_slot=selected_time_key,
                            is_member=is_member,
                            membership_type=membership_type,
                            payment_amount=price
                        )
                         
                         if booking:
                            st.balloons()
                            st.success(f"예약 완료! 예약번호: {booking.id}")
                         else:
                            st.error("해당 시간에는 이미 예약이 있습니다.")

