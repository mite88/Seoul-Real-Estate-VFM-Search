"""
Seoul Real Estate VFM Search Application
Final Version 11.2.0 - 최종 완성

주요 변경:
- results 폴더 데이터 사용
- vfm_12m → vfm_index 매핑
- 최신 데이터만 표시
- 평형 필터 추가 (초소형/소형/중형/대형)
- 3단계 VFM 등급 (0.5 미만 제외)
- 지도 마커 색상과 통계 색상 일치
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

# CSS 스타일
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
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data_simple(contract_type):
    """데이터 로딩"""
    try:
        df_vfm = load_vfm_data(contract_type=contract_type)
        df_grid = load_grid_mapping()
        df = merge_vfm_with_district(df_vfm, df_grid)

        # vfm_index를 custom_vfm으로 복사
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


def create_map(df, map_type="marker", contract_type="monthly", marker_limit=500, sort_order="desc", vfm_grades=None):
    """지도 생성"""

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

    # 좌표 유효성 검사
    df_valid = df.dropna(subset=['lat', 'lon']).copy()
    df_valid = df_valid.reset_index(drop=True)

    if len(df_valid) == 0:
        return m

    # VFM 등급별 필터링 (3단계)
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

    # VFM 분포 통계
    vfm_stats = {}
    if len(df_valid) > 0:
        vfm_values = df_valid['custom_vfm'].dropna()
        if len(vfm_values) > 0:
            vfm_stats = {
                'min': vfm_values.min(),
                'max': vfm_values.max(),
                'mean': vfm_values.mean(),
                'median': vfm_values.median(),
            }

    data_count = len(df_valid)
    display_count = min(
        marker_limit, data_count) if map_type == "marker" else data_count

    # 범례 HTML
    legend_html = f"""
    <div style="position: fixed; top: 10px; left: 50px; width: 260px; background-color: white; 
                border: 2px solid #667eea; border-radius: 10px; padding: 12px; font-size: 13px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 9999;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
                    padding: 8px; margin: -12px -12px 10px -12px; border-radius: 8px 8px 0 0;
                    font-weight: 600; text-align: center; font-size: 14px;">
            📊 VFM 지수 범례 ({'월세' if contract_type == 'monthly' else '전세'})
        </div>
        <div style="margin-bottom: 8px; padding: 8px; background: #e8f5e9; border-radius: 6px; border-left: 3px solid #4caf50;">
            <div style="font-size: 11px; color: #2e7d32; margin-bottom: 4px;"><strong>📐 VFM 계산 방법</strong></div>
            <div style="font-size: 10px; color: #1b5e20;">VFM = 미래 예상 가격 ÷ 현재 가격<br>(AI 모델 기반 12개월 후 예측)</div>
        </div>
    """

    if map_type == "marker":
        sort_label = "높은 순" if sort_order == "desc" else "낮은 순"
        selected_grades = []
        if not vfm_grades or len(vfm_grades) == 3:
            grade_text = "전체 등급"
        else:
            if 'excellent' in vfm_grades:
                selected_grades.append("🟢최우수")
            if 'good' in vfm_grades:
                selected_grades.append("🔵우수")
            if 'normal' in vfm_grades:
                selected_grades.append("🟠보통")
            grade_text = ", ".join(selected_grades)

        legend_html += f"""
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
        <div style="margin-top: 8px; padding: 6px; background: #fff3cd; border-radius: 4px; border-left: 2px solid #ffc107;">
            <div style="font-size: 10px; color: #856404;">
                📍 <strong>정렬:</strong> VFM {sort_label}<br>
                🎯 <strong>등급:</strong> {grade_text}
            </div>
        </div>
        """

    if vfm_stats:
        legend_html += f"""
        <div style="margin-top: 8px; padding: 8px; background: #fff3cd; border-radius: 6px; border-left: 3px solid #ffc107;">
            <div style="font-size: 10px; color: #856404; margin-bottom: 4px;"><strong>📊 선택 조건 분포</strong></div>
            <div style="font-size: 9px; color: #856404;">
                최소: {vfm_stats['min']:.3f} | 최대: {vfm_stats['max']:.3f}<br>
                평균: {vfm_stats['mean']:.3f} | 중앙: {vfm_stats['median']:.3f}
            </div>
        </div>
        """

    if map_type == "marker" and data_count > marker_limit:
        legend_html += f"""
        <div style="margin-top: 8px; padding: 8px; background: #ffe5e5; border-radius: 6px; border-left: 3px solid #ff4444;">
            <div style="font-size: 9px; color: #cc0000;">
                ⚠️ VFM {sort_label} {marker_limit}개만 표시<br>
                (나머지 {data_count - marker_limit:,}개 숨김)
            </div>
        </div>
        """

    legend_html += f"""
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
                gradient={0.0: 'blue', 0.3: 'cyan',
                          0.5: 'lime', 0.7: 'yellow', 1.0: 'red'}
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

        # 색상별 마커 그룹
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
            else:  # 0.5~1.0
                color = 'orange'
                icon = 'home'
                grade = '보통 (0.5~1.0)'
                marker_list = orange_markers

            # 평형 정보
            size_cat = row.get('size_category', '미분류')

            # 가격 정보
            if contract_type == 'monthly':
                deposit = row.get('deposit_amount', 0)
                rent = row.get('monthly_rent', 0)
                converted = deposit + (rent * 100)

                price_html = f"""
                    <div style='margin-bottom: 8px;'>
                        <div style='font-size: 0.75rem; color: #666; margin-bottom: 4px; font-weight: 600;'>💵 월세 정보</div>
                        <div style='display: flex; gap: 6px;'>
                            <div style='flex: 1; background: #e3f2fd; padding: 6px; border-radius: 4px;'>
                                <div style='font-size: 0.7rem; color: #1976d2;'>💰 보증금</div>
                                <div style='font-size: 0.95rem; font-weight: 700; color: #0d47a1;'>{deposit:,.0f}만</div>
                            </div>
                            <div style='flex: 1; background: #fff3e0; padding: 6px; border-radius: 4px;'>
                                <div style='font-size: 0.7rem; color: #f57c00;'>💵 월세</div>
                                <div style='font-size: 0.95rem; font-weight: 700; color: #e65100;'>{rent:,.0f}만</div>
                            </div>
                        </div>
                        <div style='font-size: 0.65rem; color: #999; margin-top: 4px; text-align: center;'>
                            (전환보증금: {converted:,.0f}만원)
                        </div>
                    </div>
                """
                prediction_html = ""
            else:
                deposit = row.get('total_deposit_median', 0)
                future_price = row.get('future_price', 0)
                price_change_pct = row.get('price_change_pct', 0)

                price_html = f"""
                    <div style='margin-bottom: 8px;'>
                        <div style='font-size: 0.75rem; color: #666; margin-bottom: 4px; font-weight: 600;'>💵 전세 정보</div>
                        <div style='background: #e8f5e9; padding: 6px; border-radius: 4px;'>
                            <div style='font-size: 0.7rem; color: #388e3c;'>💰 현재 전세가</div>
                            <div style='font-size: 0.95rem; font-weight: 700; color: #1b5e20;'>{deposit:,.0f}만원</div>
                        </div>
                    </div>
                """

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

                    price_diff = abs(future_price - deposit)

                    prediction_html = f"""
                        <div style='background: #f5f5f5; padding: 8px; border-radius: 4px; margin-bottom: 8px; 
                                    border-left: 3px solid {trend_color};'>
                            <div style='font-size: 0.7rem; color: #666; margin-bottom: 3px;'>
                                {trend_icon} <strong>12개월 후 예상</strong>
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

            # 인프라 지표
            trans_val = row.get('trans_index', 0)
            conv_val = row.get('conv_index', 0)
            env_val = row.get('env_index', 0)
            safety_val = row.get('safety_score_scaled', 0)
            crime_val = row.get('grid_crime_index', 0)

            popup_html = f"""
            <div style='width: 290px; font-family: "Segoe UI", Arial, sans-serif; position: relative;'>
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
                            <span>🛡️ 안전</span><strong style='color: #667eea;'>{safety_val:.4f}</strong>
                        </div>
                        <div style='display: flex; justify-content: space-between; padding: 2px 0;'>
                            <span>🚨 치안</span><strong style='color: #667eea;'>{crime_val:.6f}</strong>
                        </div>
                    </div>
                </div>
            </div>
            """

            if contract_type == 'monthly':
                tooltip_text = f"VFM: {vfm:.3f} | {size_cat} | 보증금: {deposit:,.0f}만 / 월세: {rent:,.0f}만"
            else:
                tooltip_text = f"VFM: {vfm:.3f} | {size_cat} | 전세: {deposit:,.0f}만"

            marker = folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=color, icon=icon, prefix='fa'),
                tooltip=tooltip_text
            )
            marker_list.append(marker)

        # 낮은 등급부터 추가 (높은 등급이 위로)
        for marker in orange_markers:
            marker.add_to(m)
        for marker in blue_markers:
            marker.add_to(m)
        for marker in green_markers:
            marker.add_to(m)

        print(f"\n{'='*60}")
        print(f"📊 마커 생성 완료 (정렬: {sort_order})")
        print(f"{'='*60}")
        print(f"🟢 초록색 (2.0+):      {len(green_markers):,}개")
        print(f"🔵 파란색 (1.0~2.0):   {len(blue_markers):,}개")
        print(f"🟠 주황색 (0.5~1.0):   {len(orange_markers):,}개")
        print(f"{'='*60}\n")

    if len(df_valid) > 0:
        m.location = [df_valid['lat'].mean(), df_valid['lon'].mean()]
        m.zoom_start = 12

    return m


def main():
    st.markdown("""
        <div class='header-container'>
            <h1 class='header-title'>🏠 Seoul Real Estate VFM Search</h1>
            <p class='header-subtitle'>500m 그리드 기반 부동산 가치 분석 시스템 | Version 11.2 (최종) | Updated: 2026-02</p>
        </div>
    """, unsafe_allow_html=True)

    if 'contract_type' not in st.session_state:
        st.session_state.contract_type = 'monthly'

    col_left, col_right = st.columns([1, 2.5])

    with col_left:
        st.markdown("""
            <div class='panel-section'>
                <div class='section-title'><span class='section-icon'>📋</span><span>계약 유형</span></div>
            </div>
        """, unsafe_allow_html=True)

        contract_type = st.radio(
            "계약 유형",
            options=['monthly', 'jeonse'],
            format_func=lambda x: '월세' if x == 'monthly' else '전세',
            label_visibility='collapsed'
        )
        st.session_state.contract_type = contract_type

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
                label_visibility='collapsed',
                help="VFM이 높은 매물부터 보려면 '높은 순'을 선택하세요"
            )

            st.markdown("**📍 마커 표시 개수**")
            marker_limit = st.slider(
                "마커 개수",
                min_value=50,
                max_value=1000,
                value=500,
                step=50,
                label_visibility='collapsed',
                help="선택한 정렬 순서대로 표시됩니다."
            )
        else:
            marker_limit = 500
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
                label_visibility='collapsed',
                help="여러 구를 선택할 수 있습니다."
            )
        else:
            selected_districts = ['전체']
            st.warning("⚠️ 구 정보를 불러올 수 없습니다.")

        st.markdown("""
            <div class='panel-section'>
                <div class='section-title'><span class='section-icon'>📏</span><span>평형 선택</span></div>
            </div>
        """, unsafe_allow_html=True)

        if not temp_df.empty and 'size_category' in temp_df.columns:
            available_sizes = temp_df['size_category'].dropna(
            ).unique().tolist()

            # 평형 순서 정렬
            size_order = ['초소형', '소형', '중형', '대형']
            available_sizes = [s for s in size_order if s in available_sizes]

            size_options = ['전체'] + available_sizes

            selected_sizes = st.multiselect(
                "평형 선택",
                options=size_options,
                default=['전체'],
                label_visibility='collapsed',
                help="여러 평형을 선택할 수 있습니다."
            )
        else:
            selected_sizes = ['전체']
            st.warning("⚠️ 평형 정보를 불러올 수 없습니다.")

        st.markdown("""
            <div class='panel-section'>
                <div class='section-title'><span class='section-icon'>💰</span><span>가격 범위 (만원)</span></div>
            </div>
        """, unsafe_allow_html=True)

        if contract_type == 'monthly':
            st.markdown("**보증금 범위**")
            deposit_range = st.slider(
                "보증금", 0, 50000, (0, 50000), step=1000, label_visibility='collapsed')
            st.markdown("**월세 범위**")
            price_range = st.slider(
                "월세", 0, 500, (0, 500), step=10, label_visibility='collapsed')
        else:
            st.markdown("**전세 범위**")
            price_range = st.slider(
                "전세", 0, 100000, (0, 100000), step=1000, label_visibility='collapsed')

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

                # 구 필터
                if '전체' not in selected_districts and len(selected_districts) > 0:
                    df_filtered = df_filtered[df_filtered['district'].isin(
                        selected_districts)]

                # 평형 필터
                if '전체' not in selected_sizes and len(selected_sizes) > 0:
                    df_filtered = df_filtered[df_filtered['size_category'].isin(
                        selected_sizes)]

                # 가격 필터
                if contract_type == 'monthly':
                    if 'deposit_amount' in df_filtered.columns and 'monthly_rent' in df_filtered.columns:
                        df_filtered = df_filtered[
                            (df_filtered['deposit_amount'] >= deposit_range[0]) &
                            (df_filtered['deposit_amount'] <= deposit_range[1]) &
                            (df_filtered['monthly_rent'] >= price_range[0]) &
                            (df_filtered['monthly_rent'] <= price_range[1])
                        ]
                else:
                    if 'total_deposit_median' in df_filtered.columns:
                        df_filtered = df_filtered[
                            (df_filtered['total_deposit_median'] >= price_range[0]) &
                            (df_filtered['total_deposit_median']
                             <= price_range[1])
                        ]

                df_filtered = df_filtered.reset_index(drop=True)

                if len(df_filtered) > 0:
                    # VFM 등급별 분포
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

                    # 평형별 분포
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

                if map_type == 'marker' and len(df_filtered) > marker_limit:
                    sort_label = "높은" if sort_order == "desc" else "낮은"
                    st.warning(f"""
                    ⚠️ **마커 표시 제한**
                    
                    검색 결과 **{len(df_filtered):,}건** 중 **VFM {sort_label} 순 {marker_limit}개**만 표시됩니다.
                    
                    💡 전체를 보려면: 마커 개수를 늘리거나 히트맵 모드로 전환하세요.
                    """)

                st.info("""
                📐 **VFM 계산 방법**
                
                **VFM = 미래 예상 가격 ÷ 현재 가격**
                
                - AI 모델 기반 12개월 후 가격 예측
                - 서울 전체 기준 절대 평가
                - VFM > 1.0: 상승 예상 (저평가)
                - VFM < 1.0: 하락 예상 (고평가)
                """)

                st.markdown("<br>", unsafe_allow_html=True)
                folium_map = create_map(
                    df_filtered, map_type, contract_type, marker_limit, sort_order, vfm_grades)
                st_folium(folium_map, width=None,
                          height=600, returned_objects=[])

                if len(df_filtered) > 0:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("📋 검색 결과 (상위 100개)")

                    cols = ['grid_id', 'district',
                            'size_category', 'custom_vfm']

                    if contract_type == 'monthly':
                        if 'deposit_amount' in df_filtered.columns:
                            cols.append('deposit_amount')
                        if 'monthly_rent' in df_filtered.columns:
                            cols.append('monthly_rent')
                    else:
                        if 'total_deposit_median' in df_filtered.columns:
                            cols.append('total_deposit_median')
                        if 'future_price' in df_filtered.columns:
                            cols.append('future_price')
                        if 'price_change_pct' in df_filtered.columns:
                            cols.append('price_change_pct')

                    cols.extend(['trans_index', 'conv_index', 'env_index',
                                'safety_score_scaled', 'grid_crime_index'])
                    cols = [c for c in cols if c in df_filtered.columns]

                    df_show = df_filtered[cols].head(100).sort_values(
                        'custom_vfm', ascending=False)

                    rename_dict = {
                        'grid_id': '그리드',
                        'district': '구',
                        'size_category': '평형',
                        'custom_vfm': 'VFM 지수',
                        'deposit_amount': '보증금(만원)',
                        'monthly_rent': '월세(만원)',
                        'total_deposit_median': '전세(만원)',
                        'future_price': '예상가(만원)',
                        'price_change_pct': '변화율(%)',
                        'trans_index': '교통',
                        'conv_index': '편의',
                        'env_index': '환경',
                        'safety_score_scaled': '안전',
                        'grid_crime_index': '치안'
                    }
                    df_show = df_show.rename(columns=rename_dict)

                    st.dataframe(df_show, height=400)

                    csv = df_show.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 CSV 다운로드",
                        data=csv,
                        file_name=f'vfm_search_{contract_type}_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv',
                        mime='text/csv'
                    )
                else:
                    st.warning("⚠️ 검색 조건에 맞는 데이터가 없습니다.")

        else:
            st.info("🔍 왼쪽 패널에서 검색 조건을 설정한 후 '검색하기' 버튼을 눌러주세요.")

            st.markdown("""
            ### 📖 VFM 지수란?
            
            **VFM (Value For Money) = 미래 예상 가격 ÷ 현재 가격**
            
            - AI 모델 기반 12개월 후 가격 예측
            - **VFM > 1.0**: 저평가 (투자 가치 높음 ↑)
            - **VFM = 1.0**: 적정 가격
            - **VFM < 1.0**: 고평가 (투자 주의)
            
            ---
            
            ### 📊 VFM 등급 기준 (3단계)
            
            - **2.0 이상**: 🟢 최우수 (강력 추천)
            - **1.0 ~ 2.0**: 🔵 우수 (투자 고려)
            - **0.5 ~ 1.0**: 🟠 보통 (신중 검토)
            
            ※ VFM 0.5 미만 데이터는 필터링되어 제외되었습니다.
            
            ---
            
            ### 📏 평형 기준
            
            - **초소형**: 40㎡ 미만 (약 12평)
            - **소형**: 40~60㎡ (약 12~18평)
            - **중형**: 60~85㎡ (약 18~26평)
            - **대형**: 85㎡ 이상 (약 26평 이상)
            """)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ 오류: {str(e)}")
        import traceback
        traceback.print_exc()
