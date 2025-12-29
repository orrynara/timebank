"""TimeBank 관리자 페이지 모듈.

시스템 현황, 예약 관리, 매출 통계를 제공합니다.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from modules.core_logic import get_system

system = get_system()

def render_admin_page():
    """관리자 탭 화면."""
    st.header("🛠️ 관리자 대시보드")
    
    tab_booking, tab_assets, tab_stats = st.tabs(["예약 현황", "자산 관리", "통계 분석"])
    
    with tab_booking:
        st.subheader("실시간 예약 내역")
        
        # --- 필터링 옵션 ---
        col1, col2 = st.columns([2, 1])
        with col1:
            # 날짜 범위 선택 (기본값: 최근 30일)
            today = datetime.now().date()
            start_date_default = today - timedelta(days=30)
            date_range = st.date_input(
                "📅 조회 기간",
                value=(start_date_default, today),
                max_value=today + timedelta(days=365) # 미래 예약도 있을 수 있으므로 넉넉히
            )
        
        with col2:
            # 회원 여부 필터
            member_filter = st.multiselect(
                "👤 회원 구분",
                options=["회원", "비회원"],
                default=["회원", "비회원"]
            )

        if system._bookings:
            # 1. 데이터 수집
            data = []
            for b in system._bookings:
                # 캠핑장 정보 조회
                campsite = next((c for c in system._campsites if c.id == b.campsite_id), None)
                c_type = campsite.type if campsite else "Unknown"
                
                # 예약 날짜 타입 보정 (문자열, datetime, date 등 혼재 가능성 대비)
                b_date = b.date
                if isinstance(b_date, str):
                    try:
                        b_date = datetime.strptime(b_date, "%Y-%m-%d").date()
                    except ValueError:
                        pass # 파싱 실패 시 원본 유지 혹은 에러 처리
                elif isinstance(b_date, datetime):
                    b_date = b_date.date()

                data.append({
                    "예약번호": b.id,
                    "모델 종류": c_type,
                    "캠핑장": b.campsite_id,
                    "고객": b.user_id,
                    "예약일자": b_date, # 필터링용 원본 데이터 (Date 객체)
                    "시간": b.time_slot,
                    "상태": b.status,
                    "회원여부": "회원" if b.is_member else "비회원",
                    "결제금액": b.payment_amount, # 정렬용 숫자
                    "생성일": b.created_at
                })
            
            df = pd.DataFrame(data)
            
            # 2. 필터링 로직
            # 2-1. 날짜 필터 (date_range가 튜플로 시작, 종료일 모두 있을 때만)
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
                df = df[(df["예약일자"] >= start_date) & (df["예약일자"] <= end_date)]
            
            # 2-2. 회원 필터
            if member_filter:
                df = df[df["회원여부"].isin(member_filter)]
            
            # 3. 화면 표시용 가공
            display_df = df.copy()
            display_df["결제금액"] = display_df["결제금액"].apply(lambda x: f"{x:,}원")
            # 생성일이 datetime 객체인 경우 포맷팅
            if not display_df.empty:
                 display_df["생성일"] = display_df["생성일"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M") if hasattr(x, 'strftime') else str(x))
            
            st.markdown(f"총 **{len(display_df)}**건의 예약이 조회되었습니다.")
            
            # 최신순 정렬 (기본) - 사용자가 컬럼 클릭으로 변경 가능
            if not display_df.empty:
                display_df = display_df.sort_values(by="생성일", ascending=False)
            
            st.dataframe(
                display_df, 
                use_container_width=True,
                column_config={
                    "예약일자": st.column_config.DateColumn("예약 날짜", format="YYYY-MM-DD"),
                },
                hide_index=True
            )
        else:
            st.info("아직 접수된 예약이 없습니다.")
            
    with tab_assets:
        st.subheader("등록된 카라반 목록")
        regions = system.get_regions()
        for r in regions:
            with st.expander(f"📍 {r.name} ({r.description})"):
                campsites = system.get_campsites_by_region(r.id)
                if campsites:
                    c_data = []
                    for c in campsites:
                        c_data.append({
                            "ID": c.id,
                            "이름": c.name,
                            "유형": c.type,
                            "기본가(평일)": f"{c.base_price_weekday:,}",
                            "기본가(주말)": f"{c.base_price_weekend:,}"
                        })
                    st.table(c_data)
                else:
                    st.write("등록된 캠핑장이 없습니다.")

    with tab_stats:
        st.subheader("매출 분석 (Simulation)")
        st.warning("데이터가 충분하지 않아 시뮬레이션 데이터를 표시합니다.")
        
        # 가상의 매출 데이터 차트
        chart_data = pd.DataFrame({
            "Month": ["1월", "2월", "3월", "4월", "5월", "6월"],
            "Revenue": [1500, 2300, 3100, 2800, 4200, 5100]
        })
        st.bar_chart(chart_data.set_index("Month"))
