"""
Data Loader Module for Seoul Real Estate VFM Analysis
서울 부동산 VFM 분석을 위한 데이터 로더 모듈
Version 11.2.0 - 완전 새 버전
"""

import pandas as pd
import numpy as np
import warnings
import streamlit as st

warnings.filterwarnings('ignore')


@st.cache_data(show_spinner=False)
def load_vfm_data(contract_type='monthly'):
    """
    VFM 데이터 로드 및 전처리
    
    Parameters:
    -----------
    contract_type : str
        'monthly' (월세) 또는 'jeonse' (전세)
    
    Returns:
    --------
    pd.DataFrame
        전처리된 VFM 데이터프레임
    """
    try:
        # 파일 경로 설정
        if contract_type == 'monthly':
            file_path = './results/vfm_monthly_history_full.csv'
        else:
            file_path = './results/vfm_jeonse_history_full.csv'

        print(f"\n{'='*80}")
        print(f"📂 파일 로딩: {file_path}")

        # CSV 파일 로드
        df = pd.read_csv(file_path)
        print(f"✅ 원본 데이터 로드 완료: {len(df):,}건")

        # 1. VFM 지수 매핑 (vfm_12m → vfm_index)
        if 'vfm_12m' in df.columns:
            df['vfm_index'] = pd.to_numeric(
                df['vfm_12m'], errors='coerce').fillna(1.0)
            print(f"✅ VFM 지수 매핑: vfm_12m → vfm_index")
        else:
            st.error("❌ vfm_12m 컬럼이 CSV에 없습니다!")
            return pd.DataFrame()

        # 2. grid_id 문자열 변환
        if 'grid_id' in df.columns:
            df['grid_id'] = df['grid_id'].astype(str).str.strip()

        # 3. 좌표 처리 (center_lat, center_lon → lat, lon)
        if 'center_lat' in df.columns and 'center_lon' in df.columns:
            df['lat'] = pd.to_numeric(df['center_lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['center_lon'], errors='coerce')
            print(f"✅ 좌표 매핑: center_lat/center_lon → lat/lon")

        # 4. 구 정보 처리 (sggnm → district)
        if 'sggnm' in df.columns:
            df['district'] = df['sggnm'].astype(str)
            df['district'] = df['district'].replace(
                ['nan', 'NaN', 'None', ''], '정보없음')
            df.loc[df['district'].isna(), 'district'] = '정보없음'
            print(f"✅ 구 정보 매핑: sggnm → district")
        else:
            df['district'] = '정보없음'

        # 5. 날짜 처리
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            df['year_month'] = df['datetime'].dt.strftime('%Y-%m')

            # 최신 데이터만 사용
            df = df.sort_values('datetime').groupby(
                ['grid_id', 'size_category'], as_index=False).last()
            print(f"✅ 최신 데이터 필터링: {len(df):,}건 (기준일: {df['datetime'].max()})")

        # 6. 가격 정보 처리
        if contract_type == 'monthly':
            # 월세
            if 'original_deposit' in df.columns:
                df['deposit_amount'] = pd.to_numeric(
                    df['original_deposit'], errors='coerce').fillna(0)
            else:
                df['deposit_amount'] = 0

            if 'monthly_rent' in df.columns:
                df['monthly_rent'] = pd.to_numeric(
                    df['monthly_rent'], errors='coerce').fillna(0)
            else:
                df['monthly_rent'] = 0
        else:
            # 전세
            if 'fair_value' in df.columns:
                df['total_deposit_median'] = pd.to_numeric(
                    df['fair_value'], errors='coerce').fillna(0)
            else:
                df['total_deposit_median'] = 0

        # 7. 예측 가격 처리 (pred_12m → future_price)
        if 'pred_12m' in df.columns:
            df['future_price'] = pd.to_numeric(
                df['pred_12m'], errors='coerce').fillna(0)
        else:
            df['future_price'] = 0

        # 8. 가격 변화율 계산
        df['price_change_pct'] = 0.0

        if contract_type == 'monthly':
            current_value = df['deposit_amount'] + (df['monthly_rent'] * 100)
            mask = (current_value > 0) & (df['future_price'] > 0)
            if mask.sum() > 0:
                df.loc[mask, 'price_change_pct'] = (
                    (df.loc[mask, 'future_price'] -
                     current_value[mask]) / current_value[mask] * 100
                ).round(2)
        else:
            mask = (df['total_deposit_median'] > 0) & (df['future_price'] > 0)
            if mask.sum() > 0:
                df.loc[mask, 'price_change_pct'] = (
                    (df.loc[mask, 'future_price'] - df.loc[mask, 'total_deposit_median']) /
                    df.loc[mask, 'total_deposit_median'] * 100
                ).round(2)

        # 9. 평형 정보 처리
        if 'size_category' in df.columns:
            df['size_category'] = df['size_category'].fillna('미분류')

        # 10. 인프라 지표 처리
        infra_cols = ['trans_index', 'conv_index', 'env_index',
                      'safety_score_scaled', 'grid_crime_index']

        for col in infra_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0

        print(f"✅ 데이터 전처리 완료")
        print(f"📊 최종 데이터: {len(df):,}건")
        print(
            f"📍 VFM 통계: min={df['vfm_index'].min():.3f}, max={df['vfm_index'].max():.3f}, mean={df['vfm_index'].mean():.3f}")
        print(f"🏘️ 구 개수: {df['district'].nunique()}개")
        print(f"{'='*80}\n")

        return df

    except FileNotFoundError:
        st.error(f"❌ 데이터 파일을 찾을 수 없습니다: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류 발생: {str(e)}")
        import traceback
        st.error(f"상세 오류:\n{traceback.format_exc()}")
        return pd.DataFrame()


def load_grid_mapping():
    """그리드-구 매핑 데이터 로드 (하위 호환성)"""
    return pd.DataFrame()


def merge_vfm_with_district(df_vfm, df_mapping):
    """VFM 데이터와 구 매핑 데이터 병합 (하위 호환성)"""
    return df_vfm


def get_data_summary(df, contract_type='monthly'):
    """데이터 요약 정보 생성"""
    if df is None or df.empty:
        return {
            'total_count': 0,
            'districts': 0,
            'grids': 0,
            'vfm_mean': 0,
            'vfm_median': 0
        }

    return {
        'total_count': len(df),
        'districts': df['district'].nunique() if 'district' in df.columns else 0,
        'grids': df['grid_id'].nunique() if 'grid_id' in df.columns else 0,
        'vfm_mean': df['vfm_index'].mean() if 'vfm_index' in df.columns else 0,
        'vfm_median': df['vfm_index'].median() if 'vfm_index' in df.columns else 0
    }


def get_grid_coordinates(grid_id):
    """특정 그리드의 좌표 반환"""
    return (None, None)


def add_district_column(df):
    """데이터프레임에 구(district) 컬럼 추가"""
    if 'district' not in df.columns:
        df['district'] = '정보없음'
    return df
