

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def create_price_forecast_chart(current_price, future_price):
    """
    가격 예측 차트 생성

    Parameters:
    -----------
    current_price : float
        현재 가격 (만원)
    future_price : float
        예측 가격 (만원)

    Returns:
    --------
    plotly.graph_objects.Figure
        가격 예측 차트
    """
    # 6개월 간격으로 데이터 생성
    months = ['현재', '3개월', '6개월', '9개월', '12개월']

    # 선형 보간으로 중간 값 생성
    price_change = future_price - current_price
    prices = [
        current_price,
        current_price + price_change * 0.25,
        current_price + price_change * 0.50,
        current_price + price_change * 0.75,
        future_price
    ]

    # 차트 생성
    fig = go.Figure()

    # 실제 가격 라인
    fig.add_trace(go.Scatter(
        x=months,
        y=prices,
        mode='lines+markers',
        name='예측 가격',
        line=dict(color='#667eea', width=3),
        marker=dict(size=10)
    ))

    # 현재 가격 기준선
    fig.add_hline(
        y=current_price,
        line_dash="dash",
        line_color="gray",
        annotation_text="현재 가격",
        annotation_position="right"
    )

    # 레이아웃 설정
    fig.update_layout(
        title='가격 예측 추세',
        xaxis_title='기간',
        yaxis_title='가격 (만원)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    return fig


def create_radar_chart(scores_dict):
    """
    레이더 차트 생성

    Parameters:
    -----------
    scores_dict : dict
        {지표명: 점수} 형태의 딕셔너리

    Returns:
    --------
    plotly.graph_objects.Figure
        레이더 차트
    """
    # 카테고리와 값 추출
    categories = list(scores_dict.keys())
    values = list(scores_dict.values())

    # 차트가 닫히도록 첫 번째 값을 마지막에 추가
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    # 차트 생성
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=2),
        marker=dict(size=8),
        name='점수'
    ))

    # 레이아웃 설정
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            )
        ),
        showlegend=False,
        title='지표별 점수',
        height=400
    )

    return fig


def create_comparison_bar_chart(grid_data, district_avg):
    """
    그리드와 구 평균 비교 막대 차트

    Parameters:
    -----------
    grid_data : dict
        그리드 데이터 {지표명: 점수}
    district_avg : dict
        구 평균 데이터 {지표명: 점수}

    Returns:
    --------
    plotly.graph_objects.Figure
        비교 막대 차트
    """
    categories = list(grid_data.keys())
    grid_values = list(grid_data.values())
    district_values = [district_avg.get(cat, 0) for cat in categories]

    fig = go.Figure()

    # 그리드 점수
    fig.add_trace(go.Bar(
        name='선택 그리드',
        x=categories,
        y=grid_values,
        marker_color='#667eea'
    ))

    # 구 평균
    fig.add_trace(go.Bar(
        name='구 평균',
        x=categories,
        y=district_values,
        marker_color='#764ba2'
    ))

    # 레이아웃
    fig.update_layout(
        title='그리드 vs 구 평균 비교',
        xaxis_title='지표',
        yaxis_title='점수',
        barmode='group',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    return fig


def create_vfm_distribution_chart(df, selected_district=None):
    """
    VFM 점수 분포 히스토그램

    Parameters:
    -----------
    df : pd.DataFrame
        VFM 데이터프레임
    selected_district : str, optional
        특정 구 선택 시 해당 구만 표시

    Returns:
    --------
    plotly.graph_objects.Figure
        분포 히스토그램
    """
    if selected_district and selected_district != '전체':
        df_filtered = df[df['district'] == selected_district].copy()
        title = f'{selected_district} VFM 점수 분포'
    else:
        df_filtered = df.copy()
        title = '서울시 전체 VFM 점수 분포'

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df_filtered['vfm_normalized'],
        nbinsx=20,
        marker_color='#667eea',
        opacity=0.7
    ))

    # 평균선 추가
    mean_vfm = df_filtered['vfm_normalized'].mean()
    fig.add_vline(
        x=mean_vfm,
        line_dash="dash",
        line_color="red",
        annotation_text=f"평균: {mean_vfm:.1f}",
        annotation_position="top"
    )

    fig.update_layout(
        title=title,
        xaxis_title='VFM 점수',
        yaxis_title='그리드 수',
        template='plotly_white',
        height=400
    )

    return fig


def create_price_by_district_chart(df, contract_type='monthly'):
    """
    구별 평균 가격 차트

    Parameters:
    -----------
    df : pd.DataFrame
        VFM 데이터프레임
    contract_type : str
        'monthly' 또는 'jeonse'

    Returns:
    --------
    plotly.graph_objects.Figure
        구별 평균 가격 차트
    """
    # 구별 평균 계산
    if contract_type == 'monthly':
        price_col = 'monthly_rent'
        title = '구별 평균 월세'
        yaxis_title = '월세 (만원)'
    else:
        price_col = 'total_deposit_median'
        title = '구별 평균 전세금'
        yaxis_title = '전세금 (만원)'

    if price_col not in df.columns:
        # 데이터가 없는 경우 빈 차트
        fig = go.Figure()
        fig.update_layout(
            title=f'{title} (데이터 없음)',
            xaxis_title='구',
            yaxis_title=yaxis_title,
            template='plotly_white',
            height=400
        )
        return fig

    # 구별 평균 계산
    district_avg = df.groupby('district')[
        price_col].mean().sort_values(ascending=False)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=district_avg.index,
        y=district_avg.values,
        marker_color='#667eea',
        text=district_avg.values.round(0),
        textposition='outside'
    ))

    fig.update_layout(
        title=title,
        xaxis_title='구',
        yaxis_title=yaxis_title,
        template='plotly_white',
        height=400,
        xaxis_tickangle=-45
    )

    return fig


def create_scatter_vfm_price(df, contract_type='monthly'):
    """
    VFM 점수 vs 가격 산점도

    Parameters:
    -----------
    df : pd.DataFrame
        VFM 데이터프레임
    contract_type : str
        'monthly' 또는 'jeonse'

    Returns:
    --------
    plotly.graph_objects.Figure
        산점도
    """
    if contract_type == 'monthly':
        price_col = 'monthly_rent'
        title = 'VFM 점수 vs 월세'
        yaxis_title = '월세 (만원)'
    else:
        price_col = 'total_deposit_median'
        title = 'VFM 점수 vs 전세금'
        yaxis_title = '전세금 (만원)'

    if price_col not in df.columns or 'vfm_normalized' not in df.columns:
        # 데이터가 없는 경우 빈 차트
        fig = go.Figure()
        fig.update_layout(
            title=f'{title} (데이터 없음)',
            xaxis_title='VFM 점수',
            yaxis_title=yaxis_title,
            template='plotly_white',
            height=400
        )
        return fig

    # NaN 제거
    df_clean = df.dropna(subset=[price_col, 'vfm_normalized'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_clean['vfm_normalized'],
        y=df_clean[price_col],
        mode='markers',
        marker=dict(
            size=6,
            color=df_clean['vfm_normalized'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="VFM 점수")
        ),
        text=df_clean['district'],
        hovertemplate='<b>구:</b> %{text}<br>' +
                      '<b>VFM:</b> %{x:.1f}<br>' +
                      f'<b>{yaxis_title}:</b> %{y:.0f}<br>' +
                      '<extra></extra>'
    ))

    fig.update_layout(
        title=title,
        xaxis_title='VFM 점수',
        yaxis_title=yaxis_title,
        template='plotly_white',
        height=400
    )

    return fig


def create_heatmap_correlation(df, features):
    """
    지표 간 상관관계 히트맵

    Parameters:
    -----------
    df : pd.DataFrame
        VFM 데이터프레임
    features : list
        상관관계를 볼 지표 리스트

    Returns:
    --------
    plotly.graph_objects.Figure
        상관관계 히트맵
    """
    # 상관관계 계산
    corr_matrix = df[features].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="상관계수")
    ))

    fig.update_layout(
        title='지표 간 상관관계',
        template='plotly_white',
        height=500,
        width=600
    )

    return fig
