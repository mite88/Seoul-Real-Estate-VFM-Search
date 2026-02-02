"""
Detail Analysis Page
상세 분석 페이지
"""

import streamlit as st
import pandas as pd
import numpy as np
from modules.visualizations import (
    create_price_forecast_chart,
    create_radar_chart,
    create_comparison_bar_chart,
    create_vfm_distribution_chart
)
from modules.data_loader import (
    load_vfm_data,
    get_grid_coordinates,
    add_district_column
)

# 페이지 설정
st.set_page_config(
    page_title="상세 분석",
    page_icon="📊",
    layout="wide"
)

# 스타일
st.markdown("""
<style>
    .main { padding: 1rem; }
    
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("""
<div class="header-container">
    <h1>📊 상세 분석</h1>
    <p>그리드별 세부 정보 및 비교 분석</p>
</div>
""", unsafe_allow_html=True)

# 데이터 로드


@st.cache_data(show_spinner=False)
def load_analysis_data(contract_type):
    """분석 데이터 로드"""
    try:
        df = load_vfm_data(contract_type)
        df = add_district_column(df)
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {str(e)}")
        return None


# 사이드바
with st.sidebar:
    st.markdown("## ⚙️ 분석 설정")

    contract_type = st.radio(
        "계약 유형",
        options=['monthly', 'jeonse'],
        format_func=lambda x: '월세' if x == 'monthly' else '전세'
    )

    st.markdown("---")

# 데이터 로드
with st.spinner('데이터 로딩 중...'):
    df = load_analysis_data(contract_type)

if df is None:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()

# 구 선택
districts = ['전체'] + sorted(df['district'].dropna().unique().tolist())

col1, col2 = st.columns([1, 2])

with col1:
    selected_district = st.selectbox(
        "📍 구 선택",
        options=districts
    )

with col2:
    # 구에 따라 그리드 필터링
    if selected_district == '전체':
        df_filtered = df
    else:
        df_filtered = df[df['district'] == selected_district]

    grid_ids = sorted(df_filtered['grid_id'].unique().tolist())

    selected_grid = st.selectbox(
        "🎯 그리드 ID 선택",
        options=grid_ids
    )

# 선택된 그리드 데이터
if selected_grid:
    grid_data = df_filtered[df_filtered['grid_id'] == selected_grid].iloc[0]

    st.markdown("---")

    # 기본 정보
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">그리드 ID</h3>
            <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0 0 0;">{grid_data['grid_id']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        district_name = grid_data.get('district', '정보 없음')
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">구</h3>
            <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0 0 0;">{district_name}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        vfm_score = grid_data.get('vfm_normalized', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">VFM 점수</h3>
            <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0 0 0;">{vfm_score:.1f}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        # 가격 정보
        if contract_type == 'monthly':
            if 'monthly_rent' in grid_data and pd.notna(grid_data['monthly_rent']):
                price_value = f"{grid_data['monthly_rent']:.0f}만원"
                price_label = "월세"
            else:
                price_value = "정보 없음"
                price_label = "월세"
        else:
            if 'total_deposit_median' in grid_data and pd.notna(grid_data['total_deposit_median']):
                price_value = f"{grid_data['total_deposit_median']:.0f}만원"
                price_label = "전세금"
            else:
                price_value = "정보 없음"
                price_label = "전세금"

        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">{price_label}</h3>
            <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0 0 0;">{price_value}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 차트 섹션
    tab1, tab2, tab3 = st.tabs(["📈 가격 분석", "🎯 지표 분석", "📊 비교 분석"])

    with tab1:
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("📈 가격 예측")

            # 현재 가격과 예측 가격 설정
            if contract_type == 'monthly':
                if 'monthly_rent' in grid_data and pd.notna(grid_data['monthly_rent']):
                    current_price = float(grid_data['monthly_rent'])
                    future_price = current_price * 1.05
                else:
                    current_price = 0
                    future_price = 0
            else:
                if 'total_deposit_median' in grid_data and pd.notna(grid_data['total_deposit_median']):
                    current_price = float(grid_data['total_deposit_median'])
                    future_price = current_price * 1.03
                else:
                    current_price = 0
                    future_price = 0

            if current_price > 0:
                fig_price = create_price_forecast_chart(
                    current_price=current_price,
                    future_price=future_price
                )
                st.plotly_chart(fig_price, width='stretch')
            else:
                st.info("가격 데이터가 없습니다.")

        with col_chart2:
            st.subheader("📊 VFM 분포")
            fig_dist = create_vfm_distribution_chart(df, selected_district)
            st.plotly_chart(fig_dist, width='stretch')

    with tab2:
        st.subheader("🎯 지표별 점수")

        # 레이더 차트용 데이터
        scores_dict = {
            "교통": grid_data.get('trans_index', 0),
            "편의시설": grid_data.get('conv_index', 0),
            "환경": grid_data.get('env_index', 0),
            "안전": grid_data.get('safety_score_scaled', 0),
            "저범죄": grid_data.get('grid_crime_index', 0),
            "가치": grid_data.get('mlp_value_score', 0)
        }

        # 0-100 범위로 정규화
        for key in scores_dict:
            if scores_dict[key] > 100:
                scores_dict[key] = 100
            elif scores_dict[key] < 0:
                scores_dict[key] = 0

        fig_radar = create_radar_chart(scores_dict)
        st.plotly_chart(fig_radar, width='stretch')

        # 상세 점수 표
        st.markdown("#### 📋 상세 점수")
        score_df = pd.DataFrame({
            '지표': list(scores_dict.keys()),
            '점수': [f"{v:.1f}" for v in scores_dict.values()]
        })
        st.dataframe(score_df, width='stretch', hide_index=True)

    with tab3:
        st.subheader("📊 그리드 vs 구 평균 비교")

        # 구 평균 계산
        if selected_district != '전체':
            district_data = df[df['district'] == selected_district]
        else:
            district_data = df

        district_avg = {
            "교통": district_data['trans_index'].mean(),
            "편의시설": district_data['conv_index'].mean(),
            "환경": district_data['env_index'].mean(),
            "안전": district_data['safety_score_scaled'].mean(),
            "저범죄": district_data['grid_crime_index'].mean(),
            "가치": district_data['mlp_value_score'].mean()
        }

        fig_comparison = create_comparison_bar_chart(scores_dict, district_avg)
        st.plotly_chart(fig_comparison, width='stretch')

        # 차이 분석
        st.markdown("#### 📈 구 평균 대비 차이")
        diff_data = []
        for key in scores_dict:
            diff = scores_dict[key] - district_avg[key]
            diff_pct = (diff / district_avg[key] *
                        100) if district_avg[key] != 0 else 0
            diff_data.append({
                '지표': key,
                '그리드 점수': f"{scores_dict[key]:.1f}",
                '구 평균': f"{district_avg[key]:.1f}",
                '차이': f"{diff:+.1f}",
                '차이(%)': f"{diff_pct:+.1f}%"
            })

        diff_df = pd.DataFrame(diff_data)
        st.dataframe(diff_df, width='stretch', hide_index=True)

else:
    st.info("그리드를 선택해주세요.")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>📊 상세 분석 페이지 | VFM 검색 시스템</p>
</div>
""", unsafe_allow_html=True)
