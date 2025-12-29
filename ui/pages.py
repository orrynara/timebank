"""TimeBank UI 상세 페이지 모듈.

각 탭별(예약, 투자자, 관리자, 스튜디오) 화면을 구성하는 컴포넌트들을 정의합니다.
"""

import streamlit as st
import pandas as pd
import datetime
import os
import glob
from modules.core_logic import get_system
from modules.image_generator import image_gen # image_manager -> image_generator로 변경

# 개별 탭 렌더링 함수 임포트
# 순환 참조 방지를 위해 booking은 여기서 정의하거나, 분리된 모듈에서 가져옴
# 기존 구조상 render_booking_page가 여기에 있었으므로, 
# ui/booking.py로 분리된 내용을 가져오는 것이 깔끔함.
# 하지만 사용자가 ui/booking.py를 별도로 수정했으므로, 여기서는 래퍼 함수만 제공하거나 
# ui/pages.py의 역할을 라우터로 변경하는 것이 좋음.

# 그러나 기존 코드 구조(launcher.py -> ui.home -> ui.pages 등)를 유지하기 위해
# ui/booking.py, ui/studio.py 등을 임포트하여 연결.

from ui.booking import render_booking_page
from ui.studio import render_studio_page

system = get_system()

def render_investor_page():
    """투자자 탭 화면."""
    st.header("📈 투자 수익률 시뮬레이터")
    st.markdown("전액 대출(자기자본 0원)로 시작하는 **월 50만원 순수익** 모델을 확인하세요.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("설정 값")
        loan = st.number_input("대출 금액 (원)", value=30000000, step=1000000)
        revenue = st.number_input("예상 월 매출 (원)", value=1800000, step=100000)
        
    with col2:
        result = system.calculate_roi(loan, revenue)
        
        st.subheader("📊 분석 결과")
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("월 순수익", f"{result['net_profit']:,} 원", delta_color="normal")
        metric_col2.metric("연 수익률 (ROI)", f"{result['roi_percent']:.1f} %")
        metric_col3.metric("월 대출이자", f"{result['interest']:,} 원", delta_color="inverse")
        
        st.progress(result['roi_percent'] / 100)
        
        st.markdown(f"""
        - **총 매출**: {result['revenue']:,} 원
        - **운영 비용**: -{result['operating_cost']:,} 원 (관리비, 공과금 등)
        - **이자 비용**: -{result['interest']:,} 원
        - **최종 순수익**: **{result['net_profit']:,} 원**
        """)
        
    st.info("💡 타임뱅크의 위탁 운영 시스템으로 관리는 신경 쓰지 마세요. 수익만 챙기시면 됩니다.")

def render_admin_page():
    """관리자 탭 화면."""
    st.header("🛠️ 관리자 대시보드")
    
    st.subheader("예약 현황")
    if system._bookings:
        df = pd.DataFrame([vars(b) for b in system._bookings])
        st.dataframe(df)
    else:
        st.write("아직 예약 내역이 없습니다.")
        
    st.subheader("카라반 관리")
    st.write("등록된 카라반 목록:")
    for c in system.get_campsites_by_region("R001") + system.get_campsites_by_region("R002") + system.get_campsites_by_region("R003"):
         with st.expander(f"{c.name} ({c.id})"):
             st.write(f"위치: {c.location_desc}")
             st.write(f"주말 가격: {c.base_price_weekend:,} 원")
