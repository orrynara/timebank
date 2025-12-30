"""TimeBank 메인 홈 UI.

- Streamlit 화면 렌더링을 담당합니다.
- 비즈니스 로직은 modules/ 패키지에서 가져옵니다.
"""

import streamlit as st
import os
import random
import datetime
from modules.utils import load_image_safe
from modules.core_logic import get_system, Unit

# UI 컴포넌트 로드
from ui.products import render_products_page
from ui.investor import render_investor_page
from ui.admin import render_admin_page
from ui.studio import render_studio_page 

def render_unit_card(unit: Unit):
    """개별 숙소 카드 렌더링"""
    system = get_system()
    # Find campsite to get location
    campsite = next((c for c in system.get_all_campsites() if any(u.id == unit.id for u in c.units)), None)
    location_name = campsite.name if campsite else ""
    
    # 간략화된 위치명 (예: '포천 산정호수 (The Base)' -> '📍 포천 산정호수점')
    simple_loc = location_name.split('(')[0].strip() + "점"

    with st.container(border=False):
        # 이미지 (이미지 경로가 있으면 로드, 없으면 플레이스홀더)
        img_path = unit.image if os.path.exists(unit.image) else "assets/img/caravan_main.jpg"
        st.image(img_path, width="stretch")
        
        # 타이틀 및 평점
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{unit.name}**")
        with col2:
            st.markdown(f"★ {unit.rating}")
            
        # 위치 정보 (CSS 클래스 적용)
        st.markdown(f"<div class='unit-location'>📍 {simple_loc}</div>", unsafe_allow_html=True)

        # 가격 (CSS 클래스 적용)
        st.markdown(f"<div class='unit-price'>₩{unit.price:,} <span style='font-size:0.8em; font-weight:400; color:#666;'>/ 박</span></div>", unsafe_allow_html=True)
        
        # 태그 (CSS 클래스 적용)
        tags_html = "".join([f"<span class='unit-tag'>{tag}</span>" for tag in unit.tags])
        st.markdown(f"<div style='margin-top:8px;'>{tags_html}</div>", unsafe_allow_html=True)
        
        # 예약 버튼 (Dialog 호출)
        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        if st.button("예약하기", key=f"btn_{unit.id}", width="stretch"):
            st.session_state['selected_unit'] = unit
            open_booking_dialog()

@st.dialog("숙소 예약")
def open_booking_dialog():
    """예약 상세 모달 (Dialog)"""
    if 'selected_unit' not in st.session_state:
        st.error("선택된 숙소가 없습니다.")
        return

    unit = st.session_state['selected_unit']
    system = get_system()
    user_id = "demo_user" # Mock User ID
    user = system.get_user(user_id)

    # 지점명 찾기
    campsite = next((c for c in system.get_all_campsites() if any(u.id == unit.id for u in c.units)), None)
    location_name = campsite.name if campsite else ""

    # Detail Modal - 3: 위치 정보 굵게 표시
    st.markdown(f"### 📍 위치: **{location_name}**")
    st.header(unit.name)
    
    # 큰 이미지
    img_path = unit.image if os.path.exists(unit.image) else "assets/img/caravan_main.jpg"
    st.image(img_path, width="stretch")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("숙소 정보")
        st.write(f"최대 인원: {unit.max_guests}명")
        st.write(f"평점: ★ {unit.rating}")
        
        st.markdown("### 편의시설")
        for tag in unit.tags:
            st.write(f"- {tag}")
            
    with col2:
        st.subheader("예약 및 결제")
        with st.form("booking_form"):
            # Booking Flow - 4: Date Range
            today = datetime.date.today()
            date_range = st.date_input(
                "체크인 - 체크아웃",
                (today, today + datetime.timedelta(days=1)),
                min_value=today,
                format="YYYY/MM/DD"
            )
            
            check_in = date_range[0] if isinstance(date_range, tuple) and len(date_range) > 0 else today
            check_out = date_range[1] if isinstance(date_range, tuple) and len(date_range) > 1 else check_in + datetime.timedelta(days=1)
            
            guests = st.number_input("인원", min_value=1, max_value=unit.max_guests, value=2)
            
            st.divider()
            
            # Booking Flow - 4: Membership Toggle
            user_type = st.radio(
                "회원 유형 선택",
                ["일반 회원", "멤버십 회원"],
                horizontal=True
            )
            is_member_selected = (user_type == "멤버십 회원")

            # --- Viral Logic: Invite Code & Points ---
            invite_code = st.text_input("초대 코드 (5% 할인)", placeholder="초대 코드 입력")
            use_points = st.checkbox(f"포인트 사용 (보유: {user.points:,} P)")
            points_to_use = 0
            if use_points:
                points_to_use = st.number_input("사용할 포인트", min_value=0, max_value=user.points, value=0, step=1000)
            
            # 예상 가격 계산
            original_total_price = unit.price # 1박 기준 (임시)
            
            if is_member_selected:
                final_price_display = 0
                st.caption("✨ 멤버십 회원 혜택 적용")
                st.info("이용권 차감 (무료)")
            else:
                final_price_display = original_total_price
                if invite_code:
                     st.caption("ℹ️ 유효한 초대 코드라면 결제 시 5% 할인이 적용됩니다.")

                st.markdown(f"#### 기본 금액: ₩{original_total_price:,}")
                if use_points and points_to_use > 0:
                    st.markdown(f"#### 포인트 사용: -₩{points_to_use:,}")
                    final_price_display -= points_to_use
            
            submitted = st.form_submit_button("결제하기", type="primary", width="stretch")
            
            if submitted:
                try:
                    # Core logic update needed to handle date range and 0 price for members
                    # Passing calculated price or letting core logic handle it
                    # Here we simulate the result since core_logic.create_booking signature was updated
                    booking = system.create_booking(
                        unit_id=unit.id, 
                        user_id=user_id, 
                        check_in=check_in, 
                        check_out=check_out,
                        guests=guests, 
                        used_points=points_to_use if not is_member_selected else 0, 
                        invite_code=invite_code,
                        payment_amount=final_price_display if is_member_selected else None,
                        is_member=is_member_selected
                    )
                    st.success("예약이 확정되었습니다!")
                    st.balloons()
                    st.markdown(f"""
                    **결제 내역**
                    - 총 결제금액: ₩{booking.final_price:,}
                    - 적립 포인트: {booking.earned_points:,} P
                    """)
                except Exception as e:
                    st.error(f"예약 실패: {e}")

def render_navbar():
    """
    고정 상단 네비게이션 바 (Glassmorphism 적용)
    - assets/style.css의 .nav-container, .nav-inner 클래스와 연동
    """
    # 네비게이션 컨테이너 시작
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    st.markdown('<div class="nav-inner">', unsafe_allow_html=True)
    
    # 2열 구조: 로고(좌측) | 메뉴(우측)
    col_logo, col_menu = st.columns([1.5, 5])
    
    # 1. 로고 영역
    with col_logo:
         logo_path = os.path.join("assets", "img", "TIMEBANK LOGO1 .png")
         if os.path.exists(logo_path):
             # 로고 이미지 (클릭 시 홈으로 이동하는 로직은 버튼으로 구현해야 하나, 이미지 자체에 링크를 걸거나 투명 버튼 오버레이 방식 사용)
             # 여기서는 심미성을 위해 이미지만 표시하고, 홈 버튼이 기능 수행
             st.image(logo_path, width=130)
         else:
             st.markdown("<h2 style='margin:0; color:#FF385C;'>TimeBank</h2>", unsafe_allow_html=True)
    
    # 2. 메뉴 영역
    with col_menu:
        # 모바일 대응을 위한 메뉴 래퍼
        st.markdown('<div class="nav-menu-area" style="display:flex; justify-content:flex-end; gap:10px;">', unsafe_allow_html=True)
        
        # 메뉴 아이템 정의
        menu_items = ["홈", "상품", "멤버십", "파트너", "관리자"]
        
        # Streamlit 컬럼을 사용하여 가로 배치 (모바일에서는 CSS로 스크롤 처리)
        # 5개 메뉴 + 여백 조정을 위해 컬럼 비율 설정
        # 우측 정렬 효과를 위해 빈 컬럼을 앞에 둘 수도 있으나, flex-end 스타일이 더 확실함
        
        cols = st.columns(len(menu_items))
        
        def set_page(page_name):
            st.session_state['current_page'] = page_name

        # 현재 페이지 상태 확인 (스타일링 용 - 현재 Streamlit 버튼 스타일링 한계로 텍스트 색상은 CSS hover에 의존)
        current_page = st.session_state.get('current_page', '홈')

        for i, item in enumerate(menu_items):
            with cols[i]:
                # 버튼 생성
                if st.button(item, key=f"nav_btn_{item}", width="stretch"):
                    set_page(item)
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True) # End nav-inner
    st.markdown('</div>', unsafe_allow_html=True) # End nav-container


def render_membership_calculator():
    """멤버십 수익 계산기"""
    st.markdown("### 💎 Future Membership Plan")
    st.markdown("연 14% 수익과 무료 숙박, 그리고 우주여행의 기회까지.")
    
    with st.container():
        st.markdown('<div class="calculator-box">', unsafe_allow_html=True)
        investment_amount = st.slider("투자 금액 (만원)", min_value=100, max_value=100000, value=3000, step=100, format="%d 만원")
        
        days = int((investment_amount / 100) * 4)
        hours = days * 24
        annual_return = int(investment_amount * 10000 * 0.14)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<p class="result-label">연간 무료 숙박</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="result-value">{days}일</p>', unsafe_allow_html=True)
            st.caption(f"총 {hours}시간 이용 가능")
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<p class="result-label">연 배당 수익 (14%)</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="result-value">₩{annual_return:,}</p>', unsafe_allow_html=True)
            st.caption("매월 현금 지급")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("프리미엄 멤버십 상담 신청", width="stretch", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

def render_my_page():
    """마이 페이지 & 파트너 (공유 점장)"""
    system = get_system()
    user_id = "demo_user"
    user = system.get_user(user_id)

    st.title(f"반갑습니다, {user.name}님!")
    
    # 1. Dashboard
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("보유 포인트 (Time Cash)", f"{user.points:,} P", delta="결제 시 현금처럼 사용")
    with col2:
        st.metric("총 누적 수익", f"{user.total_earnings:,} P", delta=f"초대 {user.referral_count}명 성공")
    with col3:
        st.metric("멤버십 등급", "VIP Member" if user.is_member else "Basic User")
    
    st.divider()

    # 2. Viral Marketing Section
    st.subheader("🚀 공유 점장 파트너 프로그램")
    if not user.is_member:
        st.info("스타터 멤버십에 가입하고 공유 점장 자격을 획득하세요! 가입 즉시 50,000 포인트 페이백!")
        if st.button("스타터 멤버십 가입 (50,000원)", type="primary"):
            system.join_membership(user_id)
            st.success("멤버십 가입 완료! 50,000P가 지급되었습니다.")
            st.rerun()
    else:
        st.success("✅ 공유 점장 자격 보유 중")
        st.markdown("친구를 초대할 때마다 **친구는 5% 할인**, 나는 **결제금액의 10% 적립!**")
        
        code_area_col, copy_btn_col = st.columns([3, 1])
        with code_area_col:
            st.text_input("나의 초대 코드", value=user.invite_code, disabled=True)
        with copy_btn_col:
            st.button("코드 복사", icon="📋", help="클립보드에 복사") # 실제 복사는 JS 필요, 여기선 UI만

    st.divider()
    
    # 3. 예약 내역
    st.subheader("내 예약 내역")
    # (실제로는 system._bookings에서 user_id로 필터링해야 함)
    my_bookings = [b for b in system._bookings if b.user_id == user_id]
    if not my_bookings:
        st.caption("아직 예약 내역이 없습니다.")
    else:
        for booking in my_bookings:
            with st.expander(f"{booking.check_in} - {booking.final_price:,}원 ({booking.status})"):
                st.write(f"예약번호: {booking.id}")
                st.write(f"적립 포인트: {booking.earned_points}")


def main() -> None:
    """메인 실행 함수."""
    
    # --- 페이지 설정 ---
    st.set_page_config(
        page_title="TimeBank: Space Age Luxury",
        page_icon="🌌",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # --- CSS 스타일 주입 ---
    # assets/style.css 파일이 존재하면 읽어서 적용
    if os.path.exists("assets/style.css"):
        with open("assets/style.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # --- Navigation Logic (Updated) ---
    render_navbar()

    # --- 라우팅 ---
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = '홈'
        
    menu_selection = st.session_state['current_page']

    if menu_selection == "홈":
        
        # 2. Hero Section (비주얼 강화)
        # Random Playlist
        video_options = [
            "assets/img/sutleSpaceCaraban01.mp4",
            "assets/img/landingSpaceCaraban001.mp4",
            "img/d059c4e1dbabeacb69d8ed21b1e17541f65ea905aac8b68c1831ea21.mp4" # Path from requirements
        ]
        
        # Pick random video
        if 'hero_video' not in st.session_state:
            st.session_state['hero_video'] = random.choice(video_options)
        
        hero_video_path = st.session_state['hero_video']
        
        # Check existence and fallback
        real_path = hero_video_path
        if not os.path.exists(real_path):
             if real_path.startswith("img/"):
                 pass # path is correct relative to workspace
             elif not os.path.exists(real_path):
                 real_path = "assets/img/hero_video.mp4"

        if os.path.exists(real_path):
            st.video(real_path, autoplay=True, loop=True, muted=True)
            # Video Overlay Text (CSS controlled via .hero-text)
            st.markdown(
                """
                <div style="text-align: center; margin-top: -300px; margin-bottom: 250px; position: relative; z-index: 1; pointer-events: none;">
                    <h1 class="hero-text">
                        우주로 떠나는 여행, TimeBank
                    </h1>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            st.image("assets/img/caravan_main.jpg", width="stretch")

        st.markdown("<br>", unsafe_allow_html=True)

        # Search Bar (In-page)
        # Since navbar is top, we can put a simple search filter here or just best picks
        # Let's keep the filter simple above cards or just show cards
        
        # Best Picks
        st.subheader("TimeBank 5대 우주 기지 (Base Camp)")
        
        # Simple Search Widgets inline
        c1, c2, c3 = st.columns(3)
        system = get_system()
        with c1:
            regions = ["지도 전체"] + [r.name for r in system.get_regions()]
            target_region_name = st.selectbox("여행지 선택", regions, label_visibility="collapsed", key="search_region")
        
        campsites = system.get_campsites_by_region(target_region_name)
        display_units = []
        for campsite in campsites:
            display_units.extend(campsite.units)

        if not display_units:
            st.info("조건에 맞는 기지가 없습니다.")
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, unit in enumerate(display_units):
                with cols[idx % 3]:
                    render_unit_card(unit)
                    st.markdown("<br>", unsafe_allow_html=True)

    elif menu_selection == "상품":
        render_products_page()
        
    elif menu_selection == "멤버십":
        st.title("멤버십 가입 (Investment)")
        render_membership_calculator()
        st.divider()
        render_investor_page()
        
    elif menu_selection == "파트너":
        render_my_page()

    elif menu_selection == "관리자":
        render_admin_page()

    # Footer
    st.divider()
    st.caption("© 2025 TimeBank Inc. All rights reserved.")

if __name__ == "__main__":
    main()
