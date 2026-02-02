# verify_grid_02028.py
"""
GRID_02028의 실제 좌표 확인 및 검증
"""

import pandas as pd
from pathlib import Path

# 1. 원본 데이터에서 GRID_02028 찾기
print("=" * 60)
print("GRID_02028 좌표 검증")
print("=" * 60)

jeonse_path = Path('output/vfm_analysis/004_jeonse_with_grid.csv')
monthly_path = Path('output/vfm_analysis/004_monthly_with_grid.csv')

# 전세 데이터 확인
if jeonse_path.exists():
    print("\n📂 전세 데이터에서 GRID_02028 검색 중...")
    df_jeonse = pd.read_csv(jeonse_path)
    grid_02028_jeonse = df_jeonse[df_jeonse['grid_id'] == 'GRID_02028']

    if not grid_02028_jeonse.empty:
        print(f"   발견: {len(grid_02028_jeonse)}건")
        print("\n   샘플 (처음 5개):")
        print(grid_02028_jeonse[['grid_id', 'lat', 'lon', 'sigungu',
              'legal_dong', 'full_address']].head().to_string(index=False))

        # 좌표 통계
        print(f"\n   좌표 통계:")
        print(f"     평균 위도: {grid_02028_jeonse['lat'].mean():.6f}")
        print(f"     평균 경도: {grid_02028_jeonse['lon'].mean():.6f}")
        print(
            f"     위도 범위: {grid_02028_jeonse['lat'].min():.6f} ~ {grid_02028_jeonse['lat'].max():.6f}")
        print(
            f"     경도 범위: {grid_02028_jeonse['lon'].min():.6f} ~ {grid_02028_jeonse['lon'].max():.6f}")

        # 구 분포
        print(f"\n   구 분포:")
        print(grid_02028_jeonse['sigungu'].value_counts())
    else:
        print("   ⚠️  GRID_02028을 찾을 수 없습니다.")

# 월세 데이터 확인
if monthly_path.exists():
    print("\n📂 월세 데이터에서 GRID_02028 검색 중...")
    df_monthly = pd.read_csv(monthly_path)
    grid_02028_monthly = df_monthly[df_monthly['grid_id'] == 'GRID_02028']

    if not grid_02028_monthly.empty:
        print(f"   발견: {len(grid_02028_monthly)}건")
        print("\n   샘플 (처음 5개):")
        print(grid_02028_monthly[['grid_id', 'lat', 'lon', 'sigungu',
              'legal_dong', 'full_address']].head().to_string(index=False))

        # 좌표 통계
        print(f"\n   좌표 통계:")
        print(f"     평균 위도: {grid_02028_monthly['lat'].mean():.6f}")
        print(f"     평균 경도: {grid_02028_monthly['lon'].mean():.6f}")
        print(
            f"     위도 범위: {grid_02028_monthly['lat'].min():.6f} ~ {grid_02028_monthly['lat'].max():.6f}")
        print(
            f"     경도 범위: {grid_02028_monthly['lon'].min():.6f} ~ {grid_02028_monthly['lon'].max():.6f}")

        # 구 분포
        print(f"\n   구 분포:")
        print(grid_02028_monthly['sigungu'].value_counts())
    else:
        print("   ⚠️  GRID_02028을 찾을 수 없습니다.")

# 2. 생성된 매핑 파일 확인
print("\n" + "=" * 60)
print("생성된 매핑 파일 확인")
print("=" * 60)

mapping_path = Path('data/grid_district_mapping.csv')
if mapping_path.exists():
    df_mapping = pd.read_csv(mapping_path)
    grid_02028_mapping = df_mapping[df_mapping['grid_id'] == 'GRID_02028']

    if not grid_02028_mapping.empty:
        print("\n매핑 파일의 GRID_02028:")
        print(grid_02028_mapping.to_string(index=False))
    else:
        print("\n⚠️  매핑 파일에 GRID_02028이 없습니다.")

# 3. 강동구 그리드 확인 (참고용)
print("\n" + "=" * 60)
print("강동구 그리드 샘플 확인")
print("=" * 60)

if mapping_path.exists():
    gangdong_grids = df_mapping[df_mapping['district'] == '강동구'].head(10)
    print("\n강동구로 매핑된 그리드 샘플 (처음 10개):")
    print(gangdong_grids.to_string(index=False))

    print(f"\n강동구 좌표 범위:")
    print(f"  위도: {df_mapping[df_mapping['district'] == '강동구']['latitude'].min():.6f} ~ {df_mapping[df_mapping['district'] == '강동구']['latitude'].max():.6f}")
    print(f"  경도: {df_mapping[df_mapping['district'] == '강동구']['longitude'].min():.6f} ~ {df_mapping[df_mapping['district'] == '강동구']['longitude'].max():.6f}")

print("\n" + "=" * 60)
