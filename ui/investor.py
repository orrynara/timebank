"""TimeBank 투자자 정보 페이지 모듈.

ROI 시뮬레이터 및 투자 정보를 제공합니다.
"""

import streamlit as st
from modules.core_logic import get_system

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
        
        # progress 값은 0.0 ~ 1.0 사이여야 함
        roi_progress = min(max(result['roi_percent'] / 100, 0.0), 1.0)
        st.progress(roi_progress)
        
        st.markdown(f"""
        - **총 매출**: {result['revenue']:,} 원
        - **운영 비용**: -{result['operating_cost']:,} 원 (관리비, 공과금 등)
        - **이자 비용**: -{result['interest']:,} 원
        - **최종 순수익**: **{result['net_profit']:,} 원**
        """)
        
    st.info("💡 타임뱅크의 위탁 운영 시스템으로 관리는 신경 쓰지 마세요. 수익만 챙기시면 됩니다.")
