# check_vfm_components.py
"""
현재 VFM 계산에 사용되는 요소 확인
"""

import pandas as pd
from pathlib import Path

print("=" * 60)
print("VFM 구성 요소 확인")
print("=" * 60)

# VFM 파일 로드
vfm_paths = [
    'output/vfm_analysis/vfm_monthly_full_2024-12.csv',
    'output/vfm_analysis/vfm_jeonse_full_2024-12.csv',
]

for vfm_path in vfm_paths:
    path_obj = Path(vfm_path)
    if path_obj.exists():
        print(f"\n📂 파일: {vfm_path}")
        print(f"   크기: {path_obj.stat().st_size / 1024 / 1024:.1f} MB")

        # 처음 몇 행만 로드
        df = pd.read_csv(path_obj, nrows=100)

        print(f"\n📋 컬럼 목록 ({len(df.columns)}개):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")

        print(f"\n📊 데이터 통계:")
        print(f"   총 행 수 (샘플): {len(df):,}")

        # VFM/점수 관련 컬럼 찾기
        score_cols = [col for col in df.columns if any(keyword in col.lower(
        ) for keyword in ['score', 'vfm', 'rank', 'grade', 'index'])]

        if score_cols:
            print(f"\n🎯 VFM/점수 관련 컬럼 ({len(score_cols)}개):")
            for col in score_cols:
                if col in df.columns:
                    print(f"  • {col}")
                    print(
                        f"    - 범위: {df[col].min():.2f} ~ {df[col].max():.2f}")
                    print(f"    - 평균: {df[col].mean():.2f}")

        # 인프라 관련 컬럼 찾기
        infra_keywords = ['subway', 'bus', 'school', 'hospital', 'park', 'convenience',
                          'mart', 'distance', 'count', 'density', 'facility', 'infrastructure']
        infra_cols = [col for col in df.columns if any(
            keyword in col.lower() for keyword in infra_keywords)]

        if infra_cols:
            print(f"\n🏗️ 인프라 관련 컬럼 ({len(infra_cols)}개):")
            for col in infra_cols:
                print(f"  • {col}")

        # 샘플 데이터
        print(f"\n📋 샘플 데이터 (처음 3개, 주요 컬럼만):")
        display_cols = ['grid_id', 'district'] + \
            score_cols[:5] if score_cols else ['grid_id', 'district']
        display_cols = [col for col in display_cols if col in df.columns]

        if display_cols:
            print(df[display_cols].head(3).to_string(index=False))

        print("\n" + "-" * 60)

# 그리드 매핑 파일도 확인
mapping_path = Path('data/grid_district_mapping.csv')
if mapping_path.exists():
    print(f"\n📂 그리드 매핑 파일: {mapping_path}")
    df_mapping = pd.read_csv(mapping_path, nrows=5)
    print(f"   컬럼: {df_mapping.columns.tolist()}")
    print(f"   샘플:")
    print(df_mapping.head(3).to_string(index=False))

print("\n" + "=" * 60)
