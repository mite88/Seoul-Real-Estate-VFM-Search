"""
Data Loader Module for Seoul Real Estate VFM Analysis
서울 부동산 VFM 분석을 위한 데이터 로더 모듈
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


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
            file_path = './output/vfm_analysis/vfm_monthly_full_2024-12_with_rent.csv'
        else:
            file_path = './output/vfm_analysis/vfm_jeonse_full_2024-12_with_rent.csv'

        # 데이터 로드
        df = pd.read_csv(file_path)

        # 필수 컬럼 체크
        required_cols = ['grid_id', 'trans_index', 'conv_index', 'env_index',
                         'safety_score_scaled', 'grid_crime_index', 'mlp_value_score']

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"필수 컬럼 누락: {missing_cols}")

        # grid_id 문자열 변환
        df['grid_id'] = df['grid_id'].astype(str).str.strip()

        # VFM 점수 계산 (누락된 경우)
        if 'vfm_score' not in df.columns or 'vfm_normalized' not in df.columns:
            # 각 지표를 0-100 범위로 정규화
            score_columns = ['trans_index', 'conv_index', 'env_index',
                             'safety_score_scaled', 'grid_crime_index', 'mlp_value_score']

            for col in score_columns:
                if col in df.columns:
                    min_val = df[col].min()
                    max_val = df[col].max()
                    if max_val > min_val:
                        df[f'{col}_norm'] = (
                            (df[col] - min_val) / (max_val - min_val)) * 100
                    else:
                        df[f'{col}_norm'] = 50.0

            # VFM 점수 계산 (평균)
            norm_cols = [
                f'{col}_norm' for col in score_columns if f'{col}_norm' in df.columns]
            df['vfm_score'] = df[norm_cols].mean(axis=1)
            df['vfm_normalized'] = df['vfm_score']  # 이미 0-100 범위

        # 가격 정보 처리
        if contract_type == 'monthly':
            # 월세의 경우
            if 'monthly_rent' in df.columns:
                df['monthly_rent'] = pd.to_numeric(
                    df['monthly_rent'], errors='coerce')
            if 'deposit_amount' in df.columns:
                df['deposit_amount'] = pd.to_numeric(
                    df['deposit_amount'], errors='coerce')
        else:
            # 전세의 경우
            if 'total_deposit_median' in df.columns:
                df['total_deposit_median'] = pd.to_numeric(
                    df['total_deposit_median'], errors='coerce')

        # 날짜 처리
        date_columns = ['contract_date', 'year_month']
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass

        return df

    except FileNotFoundError:
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {file_path}")
    except Exception as e:
        raise Exception(f"데이터 로드 중 오류 발생: {str(e)}")


def load_grid_mapping():
    """
    그리드-구 매핑 데이터 로드
    
    Returns:
    --------
    pd.DataFrame
        그리드 매핑 데이터프레임 (grid_id, district, lat, lon)
    """
    try:
        file_path = './data/grid_district_mapping.csv'
        df_mapping = pd.read_csv(file_path)

        # 필수 컬럼 체크
        required_cols = ['grid_id', 'district']
        missing_cols = [
            col for col in required_cols if col not in df_mapping.columns]
        if missing_cols:
            raise ValueError(f"매핑 파일 필수 컬럼 누락: {missing_cols}")

        # grid_id 문자열 변환
        df_mapping['grid_id'] = df_mapping['grid_id'].astype(str).str.strip()

        # 좌표 컬럼 확인 및 정리
        if 'lat' in df_mapping.columns and 'lon' in df_mapping.columns:
            df_mapping['lat'] = pd.to_numeric(
                df_mapping['lat'], errors='coerce')
            df_mapping['lon'] = pd.to_numeric(
                df_mapping['lon'], errors='coerce')
        else:
            # 좌표 컬럼이 없는 경우 경고 (출력 안 함)
            pass

        return df_mapping

    except FileNotFoundError:
        raise FileNotFoundError(f"그리드 매핑 파일을 찾을 수 없습니다: {file_path}")
    except Exception as e:
        raise Exception(f"매핑 데이터 로드 중 오류 발생: {str(e)}")


def merge_vfm_with_district(df_vfm, df_mapping):
    """
    VFM 데이터와 구 매핑 데이터 병합
    
    Parameters:
    -----------
    df_vfm : pd.DataFrame
        VFM 데이터
    df_mapping : pd.DataFrame
        그리드 매핑 데이터
    
    Returns:
    --------
    pd.DataFrame
        병합된 데이터프레임
    """
    try:
        # 병합 전 grid_id 타입 통일
        df_vfm['grid_id'] = df_vfm['grid_id'].astype(str).str.strip()
        df_mapping['grid_id'] = df_mapping['grid_id'].astype(str).str.strip()

        # 병합할 컬럼 결정
        merge_cols = ['district']
        if 'lat' in df_mapping.columns and 'lon' in df_mapping.columns:
            merge_cols.extend(['lat', 'lon'])

        # 병합 수행
        df_merged = df_vfm.merge(
            df_mapping[['grid_id'] + merge_cols],
            on='grid_id',
            how='left'
        )

        # 매칭 실패 건 확인 (경고 메시지 출력 안 함)
        unmatched = df_merged['district'].isna().sum()
        if unmatched > 0:
            # 매칭 실패 건은 '🔍 미분류'로 표시
            df_merged['district'].fillna('🔍 미분류', inplace=True)

        return df_merged

    except Exception as e:
        raise Exception(f"데이터 병합 중 오류 발생: {str(e)}")


def get_data_summary(df, contract_type='monthly'):
    """
    데이터 요약 정보 생성
    
    Parameters:
    -----------
    df : pd.DataFrame
        데이터프레임
    contract_type : str
        'monthly' 또는 'jeonse'
    
    Returns:
    --------
    dict
        요약 정보 딕셔너리
    """
    summary = {
        'total_records': len(df),
        'unique_grids': df['grid_id'].nunique(),
        'vfm_range': (df['vfm_normalized'].min(), df['vfm_normalized'].max()),
        'vfm_mean': df['vfm_normalized'].mean()
    }

    if contract_type == 'monthly':
        if 'monthly_rent' in df.columns:
            summary['monthly_rent_available'] = df['monthly_rent'].notna().sum()
            summary['monthly_rent_range'] = (
                df['monthly_rent'].min(),
                df['monthly_rent'].max()
            )
            summary['monthly_rent_mean'] = df['monthly_rent'].mean()

        if 'deposit_amount' in df.columns:
            summary['deposit_range'] = (
                df['deposit_amount'].min(),
                df['deposit_amount'].max()
            )
            summary['deposit_mean'] = df['deposit_amount'].mean()
    else:
        if 'total_deposit_median' in df.columns:
            summary['jeonse_range'] = (
                df['total_deposit_median'].min(),
                df['total_deposit_median'].max()
            )
            summary['jeonse_mean'] = df['total_deposit_median'].mean()

    return summary


def get_grid_coordinates(grid_id):
    """
    특정 그리드의 좌표 반환
    
    Parameters:
    -----------
    grid_id : str
        그리드 ID
    
    Returns:
    --------
    tuple
        (lat, lon) 또는 (None, None)
    """
    try:
        df_mapping = load_grid_mapping()
        grid_id = str(grid_id).strip()

        row = df_mapping[df_mapping['grid_id'] == grid_id]

        if len(row) > 0 and 'lat' in row.columns and 'lon' in row.columns:
            lat = row.iloc[0]['lat']
            lon = row.iloc[0]['lon']

            if pd.notna(lat) and pd.notna(lon):
                return (float(lat), float(lon))

        return (None, None)

    except:
        return (None, None)


def add_district_column(df):
    """
    데이터프레임에 구(district) 컬럼 추가
    
    Parameters:
    -----------
    df : pd.DataFrame
        VFM 데이터프레임
    
    Returns:
    --------
    pd.DataFrame
        district 컬럼이 추가된 데이터프레임
    """
    try:
        # 이미 district 컬럼이 있는 경우
        if 'district' in df.columns:
            return df

        # 매핑 데이터 로드
        df_mapping = load_grid_mapping()

        # 병합
        df_result = merge_vfm_with_district(df, df_mapping)

        return df_result

    except Exception as e:
        # 에러 발생 시 원본 반환
        if 'district' not in df.columns:
            df['district'] = '정보 없음'
        return df
