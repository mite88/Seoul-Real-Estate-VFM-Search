"""
Detail Analysis Page
Version 13.0.0 - 입지 지표 5개 + 총점, 월세 전환보증금 표시
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
    contract_type = st.radio(
        "계약 유형",
        ['monthly', 'jeonse'],
        format_func=lambda x: '월세 (전환보증금)' if x == 'monthly' else '전세'
    )

# 데이터 로드


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
col1, col2, col3 = st.columns(3)
with col1:
    districts = sorted(df['district'].unique())
    selected_district = st.selectbox("구 선택", districts)

# 구 선택 후 그리드 필터링
grid_options = df[df['district'] == selected_district]['grid_id'].unique()
with col2:
    selected_grid = st.selectbox("그리드 ID 선택", grid_options)

# 평형 필터링
with col3:
    size_options = df[df['grid_id'] == selected_grid]['size_category'].unique()
    selected_size = st.selectbox("평형 선택", size_options)

# 2. 선택된 그리드의 히스토리 데이터 추출
history_df = df[(df['grid_id'] == selected_grid) & (
    df['size_category'] == selected_size)].sort_values('datetime')

if history_df.empty:
    st.warning("선택한 그리드의 데이터가 없습니다.")
    st.stop()

# 최신 데이터 가져오기
latest_row = history_df.iloc[-1]

# 가격 라벨 설정
if contract_type == 'monthly':
    price_label = '전환보증금'
    price_note = '※ 월세를 보증금으로 전환한 금액'
else:
    price_label = '전세가'
    price_note = ''

# 3. 상세 정보 카드
st.markdown("### 📍 현재 상태 (Latest)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("VFM 지수", f"{latest_row['custom_vfm']:.3f}")
c2.metric(f"현재 {price_label}",
          f"{latest_row.get('total_deposit_median', 0):,.0f}만원")
c3.metric("AI 예측 (12개월)", f"{latest_row.get('future_price', 0):,.0f}만원")
c4.metric("예측 변화율", f"{latest_row.get('price_change_pct', 0):+.1f}%")

if contract_type == 'monthly':
    st.caption(price_note)

st.markdown("---")

# 4. 입지 지표 (5개 + 총점)
st.subheader("📊 입지 지표")

infra_col1, infra_col2 = st.columns([1, 1])

with infra_col1:
    # 레이더 차트용 데이터
    infra_labels = ['교통', '편의', '환경', '의료', '안전']
    infra_values = [
        latest_row.get('trans_index', 0),
        latest_row.get('conv_index', 0),
        latest_row.get('env_index', 0),
        latest_row.get('hospital_index', 0),
        latest_row.get('safety_score_scaled', 0)
    ]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=infra_values + [infra_values[0]],  # 닫힌 도형
        theta=infra_labels + [infra_labels[0]],
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=2),
        name='입지 지표'
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(
                infra_values) * 1.2 if max(infra_values) > 0 else 0.1])
        ),
        showlegend=False,
        height=350,
        margin=dict(l=60, r=60, t=40, b=40)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with infra_col2:

    st.markdown(f"""
    | 지표 | 점수 |
    |------|------|
    | 🚇 교통 | {latest_row.get('trans_index', 0):.4f} |
    | 🏪 편의 | {latest_row.get('conv_index', 0):.4f} |
    | 🌳 환경 | {latest_row.get('env_index', 0):.4f} |
    | 🏥 의료 | {latest_row.get('hospital_index', 0):.4f} |
    | 🛡️ 안전 | {latest_row.get('safety_score_scaled', 0):.4f} |
    """)

st.markdown("---")

# 5. AI 예측 정보
st.subheader("🔮 AI 예측 (3/6/9/12개월)")

pred_col1, pred_col2, pred_col3, pred_col4 = st.columns(4)

current_price = latest_row.get('total_deposit_median', 0)

with pred_col1:
    pred_3m = latest_row.get('pred_3m', 0)
    change_3m = ((pred_3m - current_price) / current_price *
                 100) if current_price > 0 else 0
    st.metric("3개월 후", f"{pred_3m:,.0f}만원", f"{change_3m:+.1f}%")

with pred_col2:
    pred_6m = latest_row.get('pred_6m', 0)
    change_6m = ((pred_6m - current_price) / current_price *
                 100) if current_price > 0 else 0
    st.metric("6개월 후", f"{pred_6m:,.0f}만원", f"{change_6m:+.1f}%")

with pred_col3:
    pred_9m = latest_row.get('pred_9m', 0)
    change_9m = ((pred_9m - current_price) / current_price *
                 100) if current_price > 0 else 0
    st.metric("9개월 후", f"{pred_9m:,.0f}만원", f"{change_9m:+.1f}%")

with pred_col4:
    pred_12m = latest_row.get('pred_12m', 0)
    change_12m = ((pred_12m - current_price) / current_price *
                  100) if current_price > 0 else 0
    st.metric("12개월 후", f"{pred_12m:,.0f}만원", f"{change_12m:+.1f}%")

st.markdown("---")

# 6. 차트
st.subheader("📈 시계열 트렌드")

tab1, tab2, tab3 = st.tabs(["가격 추이", "VFM 추이", "예측 비교"])

with tab1:
    fig = go.Figure()

    # 실제 가격
    fig.add_trace(go.Scatter(
        x=history_df['datetime'],
        y=history_df['total_deposit_median'],
        mode='lines+markers',
        name=f'실제 {price_label}',
        line=dict(color='blue', width=2)
    ))

    # 예측 가격 (최신 시점에서의 미래 예측)
    if latest_row.get('future_price', 0) > 0:
        future_date = latest_row['datetime'] + pd.DateOffset(months=12)
        fig.add_trace(go.Scatter(
            x=[latest_row['datetime'], future_date],
            y=[history_df.iloc[-1]['total_deposit_median'],
                latest_row['future_price']],
            mode='lines+markers',
            name='12개월 예측',
            line=dict(color='red', dash='dash', width=2)
        ))

    fig.update_layout(
        title=f"{price_label} 변동 추이 ({selected_district} - {selected_grid})",
        xaxis_title="날짜",
        yaxis_title=f"{price_label} (만원)",
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig_vfm = px.line(
        history_df,
        x='datetime',
        y='custom_vfm',
        title="VFM 지수 변화",
        markers=True
    )
    fig_vfm.add_hline(y=1.0, line_dash="dash",
                      line_color="red", annotation_text="기준점 (1.0)")
    fig_vfm.add_hline(y=2.0, line_dash="dash",
                      line_color="green", annotation_text="최우수 (2.0)")
    fig_vfm.update_layout(
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    st.plotly_chart(fig_vfm, use_container_width=True)

with tab3:
    # 예측 경로 시각화
    if current_price > 0:
        pred_dates = [
            latest_row['datetime'],
            latest_row['datetime'] + pd.DateOffset(months=3),
            latest_row['datetime'] + pd.DateOffset(months=6),
            latest_row['datetime'] + pd.DateOffset(months=9),
            latest_row['datetime'] + pd.DateOffset(months=12)
        ]
        pred_values = [
            current_price,
            latest_row.get('pred_3m', current_price),
            latest_row.get('pred_6m', current_price),
            latest_row.get('pred_9m', current_price),
            latest_row.get('pred_12m', current_price)
        ]

        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(
            x=pred_dates,
            y=pred_values,
            mode='lines+markers',
            name='AI 예측 경로',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10)
        ))

        # 현재 가격 기준선
        fig_pred.add_hline(
            y=current_price,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"현재 {price_label}"
        )

        fig_pred.update_layout(
            title="AI 예측 경로 (3/6/9/12개월)",
            xaxis_title="날짜",
            yaxis_title=f"예측 {price_label} (만원)",
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig_pred, use_container_width=True)

# 7. 데이터 테이블
with st.expander("📄 히스토리 데이터 보기"):
    display_cols = ['datetime', 'grid_id', 'district', 'size_category',
                    'total_deposit_median', 'custom_vfm', 'future_price', 'price_change_pct']
    available_cols = [col for col in display_cols if col in history_df.columns]
    st.dataframe(history_df[available_cols].sort_values(
        'datetime', ascending=False))
