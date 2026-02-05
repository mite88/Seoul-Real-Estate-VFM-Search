"""
Data Loader Module for Seoul Real Estate VFM Analysis
서울 부동산 VFM 분석을 위한 데이터 로더 모듈
Version 13.0.0 - 입지 지표 5개 + 총점 구조
"""

import pandas as pd
import numpy as np
import warnings
import streamlit as st

warnings.filterwarnings('ignore')


@st.cache_data(show_spinner=False)
def load_grid_coordinates():
    """그리드 좌표 데이터 로드"""
    try:
        grid_df = pd.read_csv('data/seoul_500m_grid_with_sggnm.csv')
        grid_df['grid_id'] = grid_df['grid_id'].astype(str).str.strip()
        print(f"✅ 그리드 좌표 로드 완료: {len(grid_df):,}건")
        return grid_df[['grid_id', 'center_lat', 'center_lon', 'sggnm']]
    except Exception as e:
        st.error(f"❌ 그리드 좌표 파일 로드 실패: {e}")
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_vfm_data(contract_type='monthly'):
    """
    VFM 데이터 로드 및 전처리
    Version 13.0.0 - 입지 지표 5개 + 총점
    """
    try:
        # 파일 경로 설정
        if contract_type == 'monthly':
            file_path = './results/vfm_monthly_hybrid_full.csv'
        else:
            file_path = './results/vfm_jeonse_hybrid_full.csv'

        print(f"\n{'='*80}")
        print(f"📂 파일 로딩: {file_path}")

        # CSV 파일 로드
        df = pd.read_csv(file_path)
        print(f"✅ 원본 데이터 로드 완료: {len(df):,}건")

        # 1. grid_id 문자열 변환
        df['grid_id'] = df['grid_id'].astype(str).str.strip()

        # 2. 그리드 좌표 데이터 로드 및 병합
        grid_coords = load_grid_coordinates()
        if not grid_coords.empty:
            df = df.merge(
                grid_coords[['grid_id', 'center_lat', 'center_lon']],
                on='grid_id',
                how='left'
            )
            df['lat'] = pd.to_numeric(df['center_lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['center_lon'], errors='coerce')
            print(f"✅ 좌표 데이터 병합 완료")
            print(f"   - 좌표 있는 데이터: {df['lat'].notna().sum():,}건")
        else:
            df['lat'] = None
            df['lon'] = None
            print("⚠️ 좌표 데이터 없음")

        # 3. VFM 지수 매핑 (vfm_12m → vfm_index)
        if 'vfm_12m' in df.columns:
            df['vfm_index'] = pd.to_numeric(
                df['vfm_12m'], errors='coerce').fillna(1.0)
            df['custom_vfm'] = df['vfm_index']
            print(f"✅ VFM 지수 매핑: vfm_12m → vfm_index")
        else:
            st.error("❌ vfm_12m 컬럼이 CSV에 없습니다!")
            return pd.DataFrame()

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
        elif 'ym' in df.columns:
            df['datetime'] = pd.to_datetime(
                df['ym'], format='%Y-%m', errors='coerce')
            df['year_month'] = df['ym']

        # 6. 가격 정보 처리 (월세/전세 동일하게 total_deposit_median 사용)
        if 'total_deposit_median' in df.columns:
            df['total_deposit_median'] = pd.to_numeric(
                df['total_deposit_median'], errors='coerce'
            ).fillna(0)
        else:
            df['total_deposit_median'] = 0

        # 7. 평균 보증금 (avg_deposit)
        if 'avg_deposit' in df.columns:
            df['avg_deposit'] = pd.to_numeric(
                df['avg_deposit'], errors='coerce').fillna(0)

        # 8. ㎡당 임대료
        if 'rent_per_m2' in df.columns:
            df['rent_per_m2'] = pd.to_numeric(
                df['rent_per_m2'], errors='coerce').fillna(0)
        else:
            df['rent_per_m2'] = 0

        # 9. 평균 면적
        if 'avg_area' in df.columns:
            df['avg_area'] = pd.to_numeric(
                df['avg_area'], errors='coerce').fillna(0)
        else:
            df['avg_area'] = 0

        # 10. 예측 가격 처리 (3m, 6m, 9m, 12m)
        pred_cols = ['pred_3m', 'pred_6m', 'pred_9m', 'pred_12m']
        for col in pred_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0

        # future_price = pred_12m
        df['future_price'] = df['pred_12m']

        # 11. 가격 변화율 계산
        df['price_change_pct'] = 0.0
        mask = (df['total_deposit_median'] > 0) & (df['future_price'] > 0)
        if mask.sum() > 0:
            df.loc[mask, 'price_change_pct'] = (
                (df.loc[mask, 'future_price'] - df.loc[mask, 'total_deposit_median']) /
                df.loc[mask, 'total_deposit_median'] * 100
            ).round(2)

        # 12. 평형 정보 처리
        if 'size_category' in df.columns:
            df['size_category'] = df['size_category'].fillna('미분류')
        else:
            df['size_category'] = '미분류'

        # 13. 입지 지표 처리 (5개 + 총점) - 치안(grid_crime_index) 제외
        infra_cols = [
            'trans_index',           # 교통
            'conv_index',            # 편의
            'env_index',             # 환경
            'hospital_index',        # 의료
            'safety_score_scaled',   # 안전
            'total_infra_score',     # 총점
            'infra_score'            # 총점 (대체)
        ]

        for col in infra_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0

        # 14. 계약 유형 표시
        df['contract_type'] = contract_type

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
    return load_grid_coordinates()


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
    grid_coords = load_grid_coordinates()
    if grid_coords.empty:
        return (None, None)

    row = grid_coords[grid_coords['grid_id'] == str(grid_id)]
    if len(row) > 0:
        return (row.iloc[0]['center_lat'], row.iloc[0]['center_lon'])
    return (None, None)


def add_district_column(df):
    """데이터프레임에 구(district) 컬럼 추가"""
    if 'district' not in df.columns:
        df['district'] = '정보없음'
    return df
