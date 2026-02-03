"""
Detail Analysis Page (V16 Integration)
히스토리 데이터를 활용한 시계열 분석 포함
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.data_loader import load_vfm_data

st.set_page_config(page_title="상세 분석", page_icon="📊", layout="wide")

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")
    contract_type = st.radio("계약 유형", [
                             'monthly', 'jeonse'], format_func=lambda x: '월세' if x == 'monthly' else '전세')

# 데이터 로드 (전체 히스토리)


@st.cache_data
def load_full_data(ctype):
    return load_vfm_data(ctype)


df = load_full_data(contract_type)

if df.empty:
    st.error("데이터가 없습니다.")
    st.stop()

# 메인 화면
st.title("📊 상세 시계열 분석")

# 1. 필터링
col1, col2 = st.columns(2)
with col1:
    districts = sorted(df['district'].unique())
    selected_district = st.selectbox("구 선택", districts)

# 구 선택 후 그리드 필터링
grid_options = df[df['district'] == selected_district]['grid_id'].unique()
with col2:
    selected_grid = st.selectbox("그리드 ID 선택", grid_options)

# 2. 선택된 그리드의 히스토리 데이터 추출
history_df = df[df['grid_id'] == selected_grid].sort_values('datetime')

if history_df.empty:
    st.warning("선택한 그리드의 데이터가 없습니다.")
    st.stop()

# 최신 데이터 가져오기
latest_row = history_df.iloc[-1]

# 3. 상세 정보 카드
st.markdown("### 📍 현재 상태 (Latest)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("VFM 지수", f"{latest_row['custom_vfm']:.3f}", delta_color="normal")
c2.metric("적정 가치 (Fair Value)", f"{latest_row.get('fair_value',0):,.0f}만")
c3.metric("AI 예측 (1년후)", f"{latest_row.get('future_price',0):,.0f}만")
if contract_type == 'monthly':
    c4.metric("현재 월세", f"{latest_row.get('monthly_rent',0):,.0f}만")
else:
    c4.metric("현재 전세", f"{latest_row.get('total_deposit_median',0):,.0f}만")

# 4. 차트 그리기
st.markdown("---")
st.subheader("📈 시계열 트렌드 (과거 ~ 미래 예측)")

# 탭 구성
tab1, tab2 = st.tabs(["가격 추이", "VFM 추이"])

with tab1:
    fig = go.Figure()

    # 실제 가격 (전세 or 환산보증금 등)
    price_col = 'total_deposit_median' if contract_type == 'jeonse' else 'monthly_rent'
    fig.add_trace(go.Scatter(x=history_df['datetime'], y=history_df[price_col],
                             mode='lines+markers', name='실제 가격', line=dict(color='blue')))

    # 적정 가치
    if 'fair_value' in history_df.columns:
        fig.add_trace(go.Scatter(x=history_df['datetime'], y=history_df['fair_value'],
                                 mode='lines', name='적정 가치 (AI)', line=dict(color='green', dash='dash')))

    # 예측 가격 (최신 시점에서의 미래 예측 점 찍기)
    if 'future_price' in latest_row:
        future_date = latest_row['datetime'] + pd.DateOffset(months=12)
        fig.add_trace(go.Scatter(x=[latest_row['datetime'], future_date],
                                 y=[history_df.iloc[-1][price_col],
                                     latest_row['future_price']],
                                 mode='lines+markers', name='미래 예측 (12M)', line=dict(color='red')))

    fig.update_layout(
        title=f"가격 변동 추이 ({selected_district} - {selected_grid})", height=500)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig_vfm = px.line(history_df, x='datetime', y='custom_vfm',
                      title="VFM 지수 변화", markers=True)
    fig_vfm.add_hline(y=1.0, line_dash="dash",
                      line_color="red", annotation_text="기준점 (1.0)")
    st.plotly_chart(fig_vfm, use_container_width=True)

# 5. 데이터 테이블
with st.expander("📄 히스토리 데이터 보기"):
    st.dataframe(history_df.sort_values('datetime', ascending=False))
