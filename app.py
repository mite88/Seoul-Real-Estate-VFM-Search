"""
Seoul Real Estate VFM Search Application
Final Version 13.0.0 - 입지 지표 5개 
주요 변경:
- 입지 지표: 5개 (치안 제외)
- 월세: 전환보증금으로 표시
- 좌표: seoul_500m_grid_with_sggnm.csv에서 매핑
"""

from modules.data_loader import (
    load_vfm_data,
    load_grid_mapping,
    merge_vfm_with_district,
    get_data_summary
)
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 페이지 설정
st.set_page_config(
    page_title="Seoul Real Estate VFM Search",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일 (기존 그대로 유지)
st.markdown("""
<style>
    .main { 
        padding: 0rem 1rem;
        background-color: #1a1a2e !important;
    }
    
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 0rem;
        background-color: #1a1a2e !important;
    }
    
    .stApp {
        background-color: #1a1a2e !important;
    }
    
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    [data-testid="column"]:first-child { 
        background: transparent !important;
    }
    
    .panel-section {
        background: white !important;
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }
    
    .section-title {
        color: #667eea !important;
        font-size: 1.1rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-icon { 
        font-size: 1.3rem;
        color: #667eea !important;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .stRadio > div {
        padding: 0.8rem;
        border-radius: 8px;
    }
    
    .stRadio label {
        color: #212529 !important;
    }
    
    .stSlider > div {
        padding: 0.8rem;
        border-radius: 8px;
    }
    
    .stSlider label {
        color: #212529 !important;
    }
    
    .stMultiSelect > div {
        padding: 0.8rem;
        border-radius: 8px;
    }
    
    .stMultiSelect label {
        color: #212529 !important;
    }
    
    .stCheckbox {
        padding: 0.2rem 0;
    }
    
    .stCheckbox label {
        color: #212529 !important;
        font-size: 0.95rem !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        color: white !important;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .stMarkdown {
        color: #fff !important;
    }
    
    .stMarkdown h3 {
        color: #667eea !important;
    }
    
    .stInfo {
        background-color: white !important;
        color: #212529 !important;
    }
    
    .stWarning {
        background-color: white !important;
        color: #212529 !important;
    }
    
    .stSuccess {
        background-color: white !important;
        color: #212529 !important;
    }
    
    .stError {
        background-color: white !important;
        color: #212529 !important;
    }
    
    .st-emotion-cache-3pwa5w li {
        color: white !important;
    }
    
    .leaflet-container a.leaflet-popup-close-button {
        top: 5px !important;
        right: 5px!important;
        font: 24px / 24px Tahoma, Verdana, sans-serif !important;
        color: #fff !important;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 8px;
        color: #495057;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Plotly 차트 텍스트 스타일 강화 */
    .js-plotly-plot .plotly text {
        fill: #000000 !important;
        font-weight: 600 !important;
    }
    
    .js-plotly-plot .plotly .xtick text,
    .js-plotly-plot .plotly .ytick text {
        fill: #000000 !important;
        font-weight: 600 !important;
    }
    
    .js-plotly-plot .plotly .gtitle {
        fill: #000000 !important;
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data_simple(contract_type):
    """데이터 로딩"""
    try:
        df_vfm = load_vfm_data(contract_type=contract_type)
        df_grid = load_grid_mapping()
        df = merge_vfm_with_district(df_vfm, df_grid)

        if 'vfm_index' in df.columns:
            df['custom_vfm'] = df['vfm_index']
        else:
            st.error("❌ vfm_index 컬럼이 없습니다!")
            return pd.DataFrame()

        return df
    except Exception as e:
        st.error(f"❌ 데이터 로딩 실패: {e}")
        import traceback
        st.code(traceback.format_exc())
        return pd.DataFrame()


def create_map(df, map_type="marker", contract_type="monthly", marker_limit=100, sort_order="desc", vfm_grades=None):
    """지도 생성 - 입지 지표 5개 """

    m = folium.Map(
        location=[37.5665, 126.9780],
        zoom_start=11,
        tiles='CartoDB positron'
    )

    if df is None or len(df) == 0:
        folium.Marker(
            [37.5665, 126.9780],
            popup="검색 결과가 없습니다",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        return m

    df_valid = df.dropna(subset=['lat', 'lon']).copy()
    df_valid = df_valid.reset_index(drop=True)

    if len(df_valid) == 0:
        return m

    # VFM 등급별 필터링
    if vfm_grades and len(vfm_grades) > 0 and len(vfm_grades) < 3:
        conditions = []
        if 'excellent' in vfm_grades:
            conditions.append(df_valid['custom_vfm'] >= 2.0)
        if 'good' in vfm_grades:
            conditions.append((df_valid['custom_vfm'] >= 1.0) & (
                df_valid['custom_vfm'] < 2.0))
        if 'normal' in vfm_grades:
            conditions.append((df_valid['custom_vfm'] >= 0.5) & (
                df_valid['custom_vfm'] < 1.0))

        if conditions:
            combined_condition = conditions[0]
            for condition in conditions[1:]:
                combined_condition = combined_condition | condition
            df_valid = df_valid[combined_condition].copy()
            df_valid = df_valid.reset_index(drop=True)

    data_count = len(df_valid)
    display_count = min(
        marker_limit, data_count) if map_type == "marker" else data_count

    # 계약 타입 라벨
    contract_label = '월세 (전환보증금)' if contract_type == 'monthly' else '전세'

    # 범례 HTML
    legend_html = f"""
    <div style="position: fixed; top: 10px; left: 50px; width: 280px; background-color: white; 
                border: 2px solid #667eea; border-radius: 10px; padding: 12px; font-size: 13px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 9999;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
                    padding: 8px; margin: -12px -12px 10px -12px; border-radius: 8px 8px 0 0;
                    font-weight: 600; text-align: center; font-size: 14px;">
            📊 VFM 지수 범례 ({contract_label})
        </div>
        <div style="margin-bottom: 6px;">
            <span style="color: green; font-size: 16px;">●</span>
            <strong style="color: green; margin-left: 5px; font-size: 12px;">2.0 이상</strong>
            <span style="font-size: 10px; color: #666; margin-left: 5px;">최우수</span>
        </div>
        <div style="margin-bottom: 6px;">
            <span style="color: blue; font-size: 16px;">●</span>
            <strong style="color: blue; margin-left: 5px; font-size: 12px;">1.0 ~ 2.0</strong>
            <span style="font-size: 10px; color: #666; margin-left: 5px;">우수</span>
        </div>
        <div style="margin-bottom: 6px;">
            <span style="color: orange; font-size: 16px;">●</span>
            <strong style="color: orange; margin-left: 5px; font-size: 12px;">0.5 ~ 1.0</strong>
            <span style="font-size: 10px; color: #666; margin-left: 5px;">보통</span>
        </div>
        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #e9ecef; font-size: 11px; color: #495057;">
            <strong>📍 전체:</strong> {data_count:,}건<br>
            <strong>🗺️ 표시:</strong> {display_count:,}건
        </div>
    </div>
    """

    m.get_root().html.add_child(folium.Element(legend_html))

    # 히트맵
    if map_type == "heatmap":
        heat_data = []
        for idx, row in df_valid.iterrows():
            vfm = row.get('custom_vfm', 1.0)
            normalized = min(vfm / 3.0, 1.0)
            heat_data.append([row['lat'], row['lon'], float(normalized)])

        if heat_data:
            HeatMap(
                heat_data,
                min_opacity=0.3,
                max_opacity=0.8,
                radius=15,
                blur=20,
                gradient={0.0: 'red', 0.3: 'orange',
                          0.5: 'yellow', 0.7: 'lime', 1.0: 'green'}
            ).add_to(m)

    # 마커
    else:
        total_count = len(df_valid)

        if total_count <= marker_limit:
            if sort_order == "desc":
                df_display = df_valid.sort_values(
                    'custom_vfm', ascending=False).copy()
            else:
                df_display = df_valid.sort_values(
                    'custom_vfm', ascending=True).copy()
            df_display = df_display.reset_index(drop=True)
        else:
            if sort_order == "desc":
                df_display = df_valid.nlargest(
                    marker_limit, 'custom_vfm').copy()
            else:
                df_display = df_valid.nsmallest(
                    marker_limit, 'custom_vfm').copy()
            df_display = df_display.reset_index(drop=True)

        green_markers = []
        blue_markers = []
        orange_markers = []

        for idx, row in df_display.iterrows():
            vfm = float(row.get('custom_vfm', 1.0))

            if vfm >= 2.0:
                color = 'green'
                icon = 'star'
                grade = '최우수 (2.0+)'
                marker_list = green_markers
            elif vfm >= 1.0:
                color = 'blue'
                icon = 'home'
                grade = '우수 (1.0~2.0)'
                marker_list = blue_markers
            else:
                color = 'orange'
                icon = 'home'
                grade = '보통 (0.5~1.0)'
                marker_list = orange_markers

            size_cat = row.get('size_category', '미분류')

            # 가격 정보
            size_cat = row.get('size_category', '미분류')
            current_price = row.get('total_deposit_median', 0)
            future_price = row.get('future_price', 0)
            price_change_pct = row.get('price_change_pct', 0)

            # NameError 해결을 위해 price_label을 여기서 정의합니다.
            if contract_type == 'monthly':
                price_label = '전환보증금'
                price_note = '<div style="font-size: 0.6rem; color: #888; margin-top: 2px;">※ 월세를 보증금으로 전환한 금액</div>'
            else:
                price_label = '전세가'
                price_note = ''

            price_html = f"""
                <div style='margin-bottom: 8px;'>
                    <div style='font-size: 0.75rem; color: #666; margin-bottom: 4px; font-weight: 600;'>
                        💵 {contract_label} 정보
                    </div>
                    <div style='background: #e8f5e9; padding: 8px; border-radius: 4px;'>
                        <div style='font-size: 0.7rem; color: #388e3c;'>💰 현재 {price_label}</div>
                        <div style='font-size: 1.1rem; font-weight: 700; color: #1b5e20;'>{current_price:,.0f}만원</div>
                        {price_note}
                    </div>
                    
                </div>
            """

            # 예측 정보 HTML
            if future_price > 0:
                if price_change_pct > 0:
                    trend_color = '#d32f2f'
                    trend_icon = '📈'
                    trend_text = '상승'
                elif price_change_pct < 0:
                    trend_color = '#1976d2'
                    trend_icon = '📉'
                    trend_text = '하락'
                else:
                    trend_color = '#757575'
                    trend_icon = '➡️'
                    trend_text = '보합'

                price_diff = abs(future_price - current_price)

                prediction_html = f"""
                    <div style='background: #f5f5f5; padding: 8px; border-radius: 4px; margin-bottom: 8px; 
                                border-left: 3px solid {trend_color};'>
                        <div style='font-size: 0.7rem; color: #666; margin-bottom: 3px;'>
                            {trend_icon} <strong>12개월 후 AI 예측</strong>
                        </div>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <div style='font-size: 0.8rem; color: {trend_color}; font-weight: 600;'>
                                    {future_price:,.0f}만원
                                </div>
                            </div>
                            <div style='background: {trend_color}; color: white; 
                                        padding: 2px 6px; border-radius: 3px; font-size: 0.7rem; font-weight: 600;'>
                                {price_change_pct:+.1f}%
                            </div>
                        </div>
                        <div style='font-size: 0.65rem; color: #999; margin-top: 2px;'>
                            예상 {trend_text}: {price_diff:,.0f}만원
                        </div>
                    </div>
                """
            else:
                prediction_html = ""

            # ✅ 입지 지표 5개
            trans_val = row.get('trans_index', 0)
            conv_val = row.get('conv_index', 0)
            env_val = row.get('env_index', 0)
            hospital_val = row.get('hospital_index', 0)
            safety_val = row.get('safety_score_scaled', 0)

            popup_html = f"""
            <div style='width: 300px; font-family: "Segoe UI", Arial, sans-serif; position: relative;'>
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 12px; border-radius: 8px 8px 0 0; 
                            margin: -10px -10px 8px -10px; position: relative;'>
                    <h4 style='margin: 0; font-size: 0.95rem; font-weight: 600; padding-right: 20px;'>
                        📍 {row.get('district', '알 수 없음')} | 📏 {size_cat}
                    </h4>
                    <p style='margin: 3px 0 0 0; font-size: 0.7rem; opacity: 0.9;'>
                        Grid ID: {row.get('grid_id', 'N/A')}
                    </p>
                </div>
                <div style='padding: 8px;'>
                    <div style='background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                                padding: 10px; border-radius: 6px; margin-bottom: 8px; text-align: center;
                                border: 2px solid {color};'>
                        <div style='font-size: 0.75rem; color: #6c757d; margin-bottom: 2px;'>VFM 지수</div>
                        <div style='font-size: 1.6rem; font-weight: 700; color: {color};'>{vfm:.3f}</div>
                        <div style='font-size: 0.65rem; color: #999; margin-top: 2px;'>{grade}</div>
                    </div>
                    {price_html}
                    {prediction_html}
                    <div style='font-size: 0.7rem; color: #495057; padding-top: 6px; border-top: 1px solid #e9ecef;'>
                        <div style='font-size: 0.75rem; color: #666; margin-bottom: 4px; font-weight: 600;'>📊 입지 지표</div>
                        <div style='display: flex; justify-content: space-between; padding: 2px 0;'>
                            <span>🚇 교통</span><strong style='color: #667eea;'>{trans_val:.4f}</strong>
                        </div>
                        <div style='display: flex; justify-content: space-between; padding: 2px 0;'>
                            <span>🏪 편의</span><strong style='color: #667eea;'>{conv_val:.4f}</strong>
                        </div>
                        <div style='display: flex; justify-content: space-between; padding: 2px 0;'>
                            <span>🌳 환경</span><strong style='color: #667eea;'>{env_val:.4f}</strong>
                        </div>
                        <div style='display: flex; justify-content: space-between; padding: 2px 0;'>
                            <span>🏥 의료</span><strong style='color: #667eea;'>{hospital_val:.4f}</strong>
                        </div>
                        <div style='display: flex; justify-content: space-between; padding: 2px 0;'>
                            <span>🛡️ 안전</span><strong style='color: #667eea;'>{safety_val:.4f}</strong>
                        </div>
                       
                    </div>
                </div>
            </div>
            """

            # 툴팁
            if contract_type == 'monthly':
                tooltip_text = f"VFM: {vfm:.3f} | {size_cat} | 전환보증금: {current_price:,.0f}만"
            else:
                tooltip_text = f"VFM: {vfm:.3f} | {size_cat} | 전세: {current_price:,.0f}만"

            marker = folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_html, max_width=320),
                icon=folium.Icon(color=color, icon=icon, prefix='fa'),
                tooltip=tooltip_text
            )
            marker_list.append(marker)

        for marker in orange_markers:
            marker.add_to(m)
        for marker in blue_markers:
            marker.add_to(m)
        for marker in green_markers:
            marker.add_to(m)

    if len(df_valid) > 0:
        m.location = [df_valid['lat'].mean(), df_valid['lon'].mean()]
        m.zoom_start = 12

    return m


def create_visualizations(df_filtered, contract_type):
    """시각화 생성 - 8개 그래프"""

    if df_filtered.empty:
        st.warning("⚠️ 표시할 데이터가 없습니다.")
        return

    # 가격 라벨 설정
    if contract_type == 'monthly':
        price_label = '전환보증금'
    else:
        price_label = '전세가'
    price_col = 'total_deposit_median'

    # 공통 마진 설정
    common_margin = dict(l=60, r=60, t=80, b=60)

    # 공통 호버 스타일
    hover_style = dict(
        bgcolor="white",
        bordercolor="white"
    )

    # 진한 색상 팔레트
    dark_colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
                   '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b']

    # 1. VFM 지수 분포 (히스토그램)
    st.subheader("📊 VFM 지수 분포")
    fig_hist = px.histogram(
        df_filtered,
        x='custom_vfm',
        nbins=50,
        title='VFM 지수 분포',
        labels={'custom_vfm': 'VFM 지수', 'count': '매물 수'},
        color_discrete_sequence=['#667eea']
    )
    fig_hist.update_layout(
        font=dict(size=18, family="Arial, sans-serif", color="#000000"),
        title_font=dict(size=26, family="Arial, sans-serif", color="#000000"),
        xaxis_title_font=dict(size=20, color="#000000"),
        yaxis_title_font=dict(size=20, color="#000000"),
        xaxis=dict(tickfont=dict(size=18, color="#000000"),
                   showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(tickfont=dict(size=18, color="#000000"),
                   showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400,
        margin=common_margin
    )
    fig_hist.update_traces(hoverlabel=hover_style)
    st.plotly_chart(fig_hist, use_container_width=True,
                    config={'displayModeBar': False})

    st.markdown("<br>", unsafe_allow_html=True)

    # 2-3. 구별 분석
    st.subheader("🗺️ 구별 분석")
    col1, col2 = st.columns(2)

    with col1:
        district_avg = df_filtered.groupby(
            'district')['custom_vfm'].mean().reset_index()
        district_avg.columns = ['구', '평균 VFM']
        district_avg = district_avg.sort_values(
            '평균 VFM', ascending=False).head(10)

        fig_district = px.bar(
            district_avg,
            x='구',
            y='평균 VFM',
            title='구별 평균 VFM (상위 10개)',
            color='평균 VFM',
            color_continuous_scale='Viridis'
        )
        fig_district.update_layout(
            font=dict(size=16, family="Arial, sans-serif", color="#000000"),
            title_font=dict(
                size=22, family="Arial, sans-serif", color="#000000"),
            xaxis=dict(tickfont=dict(size=14, color="#000000")),
            yaxis=dict(tickfont=dict(size=14, color="#000000")),
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False,
            height=400,
            margin=common_margin
        )
        fig_district.update_traces(hoverlabel=hover_style)
        st.plotly_chart(fig_district, use_container_width=True,
                        config={'displayModeBar': False})

    with col2:
        district_count = df_filtered['district'].value_counts().head(
            10).reset_index()
        district_count.columns = ['구', '매물 수']

        fig_pie = px.pie(
            district_count,
            values='매물 수',
            names='구',
            title='구별 매물 수 (상위 10개)',
            color_discrete_sequence=dark_colors
        )
        fig_pie.update_layout(
            font=dict(size=16, family="Arial, sans-serif", color="#000000"),
            title_font=dict(
                size=22, family="Arial, sans-serif", color="#000000"),
            paper_bgcolor='white',
            height=400,
            margin=common_margin
        )
        fig_pie.update_traces(
            textfont=dict(size=14, color="white"),
            textinfo='percent+label',
            hoverlabel=hover_style
        )
        st.plotly_chart(fig_pie, use_container_width=True,
                        config={'displayModeBar': False})

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. 평형별 평균 VFM
    st.subheader("📏 평형별 평균 VFM")
    size_avg = df_filtered.groupby('size_category')[
        'custom_vfm'].mean().reset_index()
    size_avg.columns = ['평형', '평균 VFM']
    size_order = ['초소형', '소형', '중형', '대형']
    size_avg['평형'] = pd.Categorical(
        size_avg['평형'], categories=size_order, ordered=True)
    size_avg = size_avg.sort_values('평형')

    fig_size = px.bar(
        size_avg,
        x='평형',
        y='평균 VFM',
        title='평형별 평균 VFM',
        color='평균 VFM',
        color_continuous_scale='Blues'
    )
    fig_size.update_layout(
        font=dict(size=18, family="Arial, sans-serif", color="#000000"),
        title_font=dict(size=26, family="Arial, sans-serif", color="#000000"),
        xaxis=dict(tickfont=dict(size=18, color="#000000")),
        yaxis=dict(tickfont=dict(size=18, color="#000000")),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
        height=400,
        margin=common_margin
    )
    fig_size.update_traces(hoverlabel=hover_style)
    st.plotly_chart(fig_size, use_container_width=True,
                    config={'displayModeBar': False})

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. 가격 vs VFM (산점도)
    st.subheader(f"💰 {price_label} vs VFM")
    if price_col in df_filtered.columns:
        sample_df = df_filtered.sample(min(1000, len(df_filtered)))

        fig_price = px.scatter(
            sample_df,
            x=price_col,
            y='custom_vfm',
            title=f'{price_label} vs VFM',
            labels={price_col: f'{price_label} (만원)', 'custom_vfm': 'VFM 지수'},
            color='custom_vfm',
            color_continuous_scale='RdYlGn',
            opacity=0.7
        )
        fig_price.update_traces(marker=dict(size=8), hoverlabel=hover_style)
        fig_price.update_layout(
            font=dict(size=18, family="Arial, sans-serif", color="#000000"),
            title_font=dict(
                size=26, family="Arial, sans-serif", color="#000000"),
            xaxis=dict(tickfont=dict(size=16, color="#000000"),
                       showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(tickfont=dict(size=16, color="#000000"),
                       showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=450,
            margin=common_margin,
            coloraxis_colorbar=dict(title=dict(text="VFM", font=dict(
                size=16, color="#000000")), tickfont=dict(size=14, color="#000000"))
        )
        st.plotly_chart(fig_price, use_container_width=True,
                        config={'displayModeBar': False})

    st.markdown("<br>", unsafe_allow_html=True)

    # 6. 인프라 종합 vs VFM (산점도)
    st.subheader("🏗️ 인프라 종합 점수 vs VFM")
    if 'infra_score' in df_filtered.columns or 'total_infra_score' in df_filtered.columns:
        infra_col = 'infra_score' if 'infra_score' in df_filtered.columns else 'total_infra_score'
        sample_df = df_filtered.sample(min(1000, len(df_filtered)))

        fig_infra = px.scatter(
            sample_df,
            x=infra_col,
            y='custom_vfm',
            title='인프라 종합 점수 vs VFM',
            labels={infra_col: '인프라 종합 점수', 'custom_vfm': 'VFM 지수'},
            color='custom_vfm',
            color_continuous_scale='RdYlGn',
            opacity=0.7
        )
        fig_infra.update_traces(marker=dict(size=8), hoverlabel=hover_style)
        fig_infra.update_layout(
            font=dict(size=18, family="Arial, sans-serif", color="#000000"),
            title_font=dict(
                size=26, family="Arial, sans-serif", color="#000000"),
            xaxis=dict(tickfont=dict(size=16, color="#000000"),
                       showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(tickfont=dict(size=16, color="#000000"),
                       showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=450,
            margin=common_margin,
            coloraxis_colorbar=dict(title=dict(text="VFM", font=dict(
                size=16, color="#000000")), tickfont=dict(size=14, color="#000000"))
        )
        st.plotly_chart(fig_infra, use_container_width=True,
                        config={'displayModeBar': False})

    # ========== 예측 관련 시각화 ==========
    st.markdown("---")
    st.subheader("🔮 AI 예측 분석")

    col1, col2 = st.columns(2)

    # 7. 기간별 예측 비교 (박스플롯) - 호버 비활성화 + 수치 텍스트 표시
    with col1:
        pred_cols = []
        pred_labels = []

        if 'pred_3m' in df_filtered.columns:
            pred_cols.append('pred_3m')
            pred_labels.append('3개월')
        if 'pred_6m' in df_filtered.columns:
            pred_cols.append('pred_6m')
            pred_labels.append('6개월')
        if 'pred_9m' in df_filtered.columns:
            pred_cols.append('pred_9m')
            pred_labels.append('9개월')
        if 'pred_12m' in df_filtered.columns:
            pred_cols.append('pred_12m')
            pred_labels.append('12개월')

        if pred_cols:
            pred_stats = []
            pred_change_data = []

            for col, label in zip(pred_cols, pred_labels):
                mask = (df_filtered[price_col] > 0) & (df_filtered[col] > 0)
                change_pct = ((df_filtered.loc[mask, col] - df_filtered.loc[mask,
                              price_col]) / df_filtered.loc[mask, price_col] * 100)
                change_pct = change_pct[(
                    change_pct >= -100) & (change_pct <= 100)]

                if len(change_pct) > 0:
                    pred_stats.append({
                        'label': label,
                        'median': change_pct.median(),
                        'q1': change_pct.quantile(0.25),
                        'q3': change_pct.quantile(0.75)
                    })

                for val in change_pct:
                    pred_change_data.append({'기간': label, '변화율': val})

            pred_df = pd.DataFrame(pred_change_data)

            if not pred_df.empty:
                fig_box = px.box(
                    pred_df,
                    x='기간',
                    y='변화율',
                    title='기간별 예측 변화율 분포',
                    labels={'기간': '예측 기간', '변화율': '변화율 (%)'},
                    color='기간',
                    color_discrete_sequence=[
                        '#3498db', '#2ecc71', '#f39c12', '#e74c3c']
                )
                fig_box.add_hline(y=0, line_dash="dash",
                                  line_color="black", line_width=1)

                # 각 박스플롯 위에 중앙값 텍스트 추가
                for stat in pred_stats:
                    fig_box.add_annotation(
                        x=stat['label'],
                        y=stat['q3'] + 8,
                        text=f"중앙값: {stat['median']:.1f}%",
                        showarrow=False,
                        font=dict(size=11, color="black", family="Arial"),
                        bgcolor="white",
                        bordercolor="gray",
                        borderwidth=1,
                        borderpad=3
                    )

                fig_box.update_layout(
                    font=dict(size=16, family="Arial, sans-serif",
                              color="#000000"),
                    title_font=dict(
                        size=22, family="Arial, sans-serif", color="#000000"),
                    xaxis=dict(tickfont=dict(size=14, color="#000000")),
                    yaxis=dict(
                        tickfont=dict(size=14, color="#000000"),
                        showgrid=True,
                        gridcolor='rgba(0,0,0,0.1)',
                        range=[-80, 80]
                    ),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    showlegend=False,
                    height=450,
                    margin=common_margin
                )
                fig_box.update_traces(hoverinfo='skip', hovertemplate=None)
                st.plotly_chart(fig_box, use_container_width=True,
                                config={'displayModeBar': False})

    # 8. 구별 예측 상승률 TOP 10 (막대)
    with col2:
        if 'price_change_pct' in df_filtered.columns:
            filtered_for_district = df_filtered[(
                df_filtered['price_change_pct'] >= -100) & (df_filtered['price_change_pct'] <= 100)]
            district_pred = filtered_for_district.groupby(
                'district')['price_change_pct'].mean().reset_index()
            district_pred.columns = ['구', '평균 예측 변화율']
            district_pred = district_pred.sort_values(
                '평균 예측 변화율', ascending=False).head(10)

            colors = ['#e74c3c' if x >
                      0 else '#3498db' for x in district_pred['평균 예측 변화율']]

            fig_district_pred = px.bar(
                district_pred,
                x='구',
                y='평균 예측 변화율',
                title='구별 12개월 예측 상승률 TOP 10',
                labels={'구': '구', '평균 예측 변화율': '평균 변화율 (%)'},
            )
            fig_district_pred.update_traces(
                marker_color=colors, hoverlabel=hover_style)
            fig_district_pred.add_hline(
                y=0, line_dash="dash", line_color="black", line_width=1)
            fig_district_pred.update_layout(
                font=dict(size=16, family="Arial, sans-serif",
                          color="#000000"),
                title_font=dict(
                    size=22, family="Arial, sans-serif", color="#000000"),
                xaxis=dict(tickfont=dict(size=14, color="#000000")),
                yaxis=dict(tickfont=dict(size=14, color="#000000"),
                           showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                plot_bgcolor='white',
                paper_bgcolor='white',
                height=450,
                margin=common_margin
            )
            st.plotly_chart(fig_district_pred, use_container_width=True, config={
                            'displayModeBar': False})


def main():
    st.markdown("""
        <div class='header-container'>
            <h1 class='header-title'>🏠 Seoul Real Estate VFM Search</h1>
            <p class='header-subtitle'>500m 그리드 기반 부동산 가치 분석 시스템 | Version 13.0 | Updated: 2026-02</p>
        </div>
    """, unsafe_allow_html=True)

    if 'contract_type' not in st.session_state:
        st.session_state.contract_type = 'monthly'

    col_left, col_right = st.columns([1, 2.5])

    with col_left:
        # 탭 추가 (상단)
        view_tab = st.radio(
            "보기 모드",
            options=['🗺️ 지도', '📊 시각화'],
            horizontal=True,
            label_visibility='collapsed'
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
            <div class='panel-section'>
                <div class='section-title'><span class='section-icon'>📋</span><span>계약 유형</span></div>
            </div>
        """, unsafe_allow_html=True)

        contract_type = st.radio(
            "계약 유형",
            options=['monthly', 'jeonse'],
            format_func=lambda x: '월세 (전환보증금)' if x == 'monthly' else '전세',
            label_visibility='collapsed'
        )
        st.session_state.contract_type = contract_type

        # 지도 설정 (지도 탭에서만 표시)
        if view_tab == '🗺️ 지도':
            st.markdown("""
                <div class='panel-section'>
                    <div class='section-title'><span class='section-icon'>🗺️</span><span>지도 설정</span></div>
                </div>
            """, unsafe_allow_html=True)

            map_type = st.radio(
                "지도 표시 방식",
                options=['marker', 'heatmap'],
                format_func=lambda x: '📍 마커' if x == 'marker' else '🔥 히트맵',
                label_visibility='collapsed'
            )

            if map_type == 'marker':
                st.markdown("**📊 VFM 정렬**")
                sort_order = st.radio(
                    "정렬 순서",
                    options=['desc', 'asc'],
                    format_func=lambda x: '⬇️ 높은 순 (추천)' if x == 'desc' else '⬆️ 낮은 순',
                    label_visibility='collapsed'
                )

                st.markdown("**📍 마커 표시 개수**")
                marker_limit = st.slider(
                    "마커 개수",
                    min_value=50,
                    max_value=1000,
                    value=100,
                    step=50,
                    label_visibility='collapsed'
                )
            else:
                marker_limit = 100
                sort_order = 'desc'
        else:
            map_type = 'marker'
            marker_limit = 100
            sort_order = 'desc'

        st.markdown("""
            <div class='panel-section'>
                <div class='section-title'><span class='section-icon'>🎯</span><span>VFM 등급 선택</span></div>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            show_excellent = st.checkbox(
                "🟢 최우수(2.0↑)", value=True, key="excellent")

        with col2:
            show_good = st.checkbox("🔵 우수(1.0~2.0)", value=True, key="good")

        with col3:
            show_normal = st.checkbox(
                "🟠 보통(0.5~1.0)", value=True, key="normal")

        vfm_grades = []
        if show_excellent:
            vfm_grades.append('excellent')
        if show_good:
            vfm_grades.append('good')
        if show_normal:
            vfm_grades.append('normal')

        if len(vfm_grades) == 0:
            st.warning("⚠️ 최소 하나의 등급을 선택해주세요!")
            vfm_grades = ['excellent', 'good', 'normal']

        st.markdown("""
            <div class='panel-section'>
                <div class='section-title'><span class='section-icon'>📍</span><span>지역 선택 (구)</span></div>
            </div>
        """, unsafe_allow_html=True)

        with st.spinner('구 목록 로딩 중...'):
            temp_df = load_data_simple(contract_type)

        if not temp_df.empty and 'district' in temp_df.columns:
            available_districts = sorted(
                temp_df['district'].dropna().unique().tolist())
            district_options = ['전체'] + available_districts

            selected_districts = st.multiselect(
                "구 선택",
                options=district_options,
                default=['전체'],
                label_visibility='collapsed'
            )
        else:
            selected_districts = ['전체']

        st.markdown("""
            <div class='panel-section'>
                <div class='section-title'><span class='section-icon'>📏</span><span>평형 선택</span></div>
            </div>
        """, unsafe_allow_html=True)

        if not temp_df.empty and 'size_category' in temp_df.columns:
            available_sizes = temp_df['size_category'].dropna(
            ).unique().tolist()
            size_order = ['초소형', '소형', '중형', '대형']
            available_sizes = [s for s in size_order if s in available_sizes]
            size_options = ['전체'] + available_sizes

            selected_sizes = st.multiselect(
                "평형 선택",
                options=size_options,
                default=['전체'],
                label_visibility='collapsed'
            )
        else:
            selected_sizes = ['전체']

        st.markdown("""
            <div class='panel-section'>
                <div class='section-title'><span class='section-icon'>💰</span><span>가격 범위 (만원)</span></div>
            </div>
        """, unsafe_allow_html=True)

        # 가격 필터링
        if contract_type == 'monthly':
            st.markdown("**전환보증금 범위**")
            st.caption("※ 월세를 보증금으로 전환한 금액")
        else:
            st.markdown("**전세 범위**")

        price_range = st.slider(
            "가격", 0, 100000, (0, 100000), step=1000, label_visibility='collapsed'
        )

        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🔍 검색하기")

    with col_right:
        if search_btn:
            with st.spinner('🔄 데이터 로딩 중...'):
                df = load_data_simple(contract_type)

            if df.empty:
                st.error("❌ 데이터를 불러올 수 없습니다.")
            else:
                df_filtered = df.copy()

                if '전체' not in selected_districts and len(selected_districts) > 0:
                    df_filtered = df_filtered[df_filtered['district'].isin(
                        selected_districts)]

                if '전체' not in selected_sizes and len(selected_sizes) > 0:
                    df_filtered = df_filtered[df_filtered['size_category'].isin(
                        selected_sizes)]

                # 가격 필터링
                if 'total_deposit_median' in df_filtered.columns:
                    df_filtered = df_filtered[
                        (df_filtered['total_deposit_median'] >= price_range[0]) &
                        (df_filtered['total_deposit_median'] <= price_range[1])
                    ]

                df_filtered = df_filtered.reset_index(drop=True)

                if len(df_filtered) > 0:
                    orange_count = len(df_filtered[(df_filtered['custom_vfm'] >= 0.5) & (
                        df_filtered['custom_vfm'] < 1.0)])
                    blue_count = len(df_filtered[(df_filtered['custom_vfm'] >= 1.0) & (
                        df_filtered['custom_vfm'] < 2.0)])
                    green_count = len(
                        df_filtered[df_filtered['custom_vfm'] >= 2.0])

                    st.write("### 🎨 VFM 등급별 분포")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); 
                                    padding: 1rem; border-radius: 10px; text-align: center; 
                                    box-shadow: 0 2px 8px rgba(46,204,113,0.4);'>
                            <div style='color: white; font-size: 0.8rem; margin-bottom: 0.3rem;'>🟢 최우수</div>
                            <div style='color: white; font-size: 1.8rem; font-weight: 700;'>{green_count:,}개</div>
                            <div style='color: rgba(255,255,255,0.9); font-size: 0.75rem; margin-top: 0.3rem;'>
                                {'2.0 이상' if show_excellent else '필터링됨'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); 
                                    padding: 1rem; border-radius: 10px; text-align: center; 
                                    box-shadow: 0 2px 8px rgba(52,152,219,0.4);'>
                            <div style='color: white; font-size: 0.8rem; margin-bottom: 0.3rem;'>🔵 우수</div>
                            <div style='color: white; font-size: 1.8rem; font-weight: 700;'>{blue_count:,}개</div>
                            <div style='color: rgba(255,255,255,0.9); font-size: 0.75rem; margin-top: 0.3rem;'>
                                {'1.0~2.0' if show_good else '필터링됨'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #e67e22 0%, #d35400 100%); 
                                    padding: 1rem; border-radius: 10px; text-align: center; 
                                    box-shadow: 0 2px 8px rgba(230,126,34,0.4);'>
                            <div style='color: white; font-size: 0.8rem; margin-bottom: 0.3rem;'>🟠 보통</div>
                            <div style='color: white; font-size: 1.8rem; font-weight: 700;'>{orange_count:,}개</div>
                            <div style='color: rgba(255,255,255,0.9); font-size: 0.75rem; margin-top: 0.3rem;'>
                                {'0.5~1.0' if show_normal else '필터링됨'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    if 'size_category' in df_filtered.columns:
                        st.write("### 📏 평형별 분포")
                        col1, col2, col3, col4 = st.columns(4)

                        size_counts = df_filtered['size_category'].value_counts(
                        )

                        with col1:
                            count = size_counts.get('초소형', 0)
                            st.metric("🏠 초소형", f"{count:,}개", delta="<40㎡")
                        with col2:
                            count = size_counts.get('소형', 0)
                            st.metric("🏡 소형", f"{count:,}개", delta="40~60㎡")
                        with col3:
                            count = size_counts.get('중형', 0)
                            st.metric("🏘️ 중형", f"{count:,}개", delta="60~85㎡")
                        with col4:
                            count = size_counts.get('대형', 0)
                            st.metric("🏰 대형", f"{count:,}개", delta="85㎡+")

                st.markdown("<br>", unsafe_allow_html=True)

                # 탭에 따라 다른 내용 표시
                if view_tab == '🗺️ 지도':
                    if map_type == 'marker' and len(df_filtered) > marker_limit:
                        sort_label = "높은" if sort_order == "desc" else "낮은"
                        st.warning(
                            f"⚠️ 검색 결과 **{len(df_filtered):,}건** 중 **VFM {sort_label} 순 {marker_limit}개**만 표시됩니다.")

                    folium_map = create_map(
                        df_filtered, map_type, contract_type, marker_limit, sort_order, vfm_grades)
                    st_folium(folium_map, width=None,
                              height=600, returned_objects=[])

                else:  # 시각화 탭
                    create_visualizations(df_filtered, contract_type)

        else:
            st.info("🔍 왼쪽 패널에서 검색 조건을 설정한 후 '검색하기' 버튼을 눌러주세요.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ 오류: {str(e)}")
        import traceback
        traceback.print_exc()
