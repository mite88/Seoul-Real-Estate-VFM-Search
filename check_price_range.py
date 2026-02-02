import pandas as pd

print("="*70)
print("그리드 매칭 분석")
print("="*70)

# 1. VFM 데이터 로드
df_monthly = pd.read_csv(
    './output/vfm_analysis/vfm_monthly_full_2024-12_with_rent.csv')
df_jeonse = pd.read_csv(
    './output/vfm_analysis/vfm_jeonse_full_2024-12_with_rent.csv')

print(f"\n[VFM 데이터]")
print(
    f"  월세: {len(df_monthly):,}건, 고유 그리드: {df_monthly['grid_id'].nunique()}개")
print(f"  전세: {len(df_jeonse):,}건, 고유 그리드: {df_jeonse['grid_id'].nunique()}개")

# 2. 그리드 매핑 로드
df_mapping = pd.read_csv('./data/grid_district_mapping.csv')
print(f"\n[그리드 매핑]")
print(f"  총 {len(df_mapping):,}개 그리드")
print(f"  컬럼: {df_mapping.columns.tolist()}")

# 3. VFM에 있는 그리드 vs 매핑에 있는 그리드
monthly_grids = set(df_monthly['grid_id'].unique())
jeonse_grids = set(df_jeonse['grid_id'].unique())
mapping_grids = set(df_mapping['grid_id'].unique())

# 매칭 안 되는 그리드
missing_monthly = monthly_grids - mapping_grids
missing_jeonse = jeonse_grids - mapping_grids

print(f"\n[매칭 분석]")
print(f"  월세 그리드: {len(monthly_grids)}개")
print(f"  전세 그리드: {len(jeonse_grids)}개")
print(f"  매핑 그리드: {len(mapping_grids)}개")
print(f"  월세 매칭 안 됨: {len(missing_monthly)}개")
print(f"  전세 매칭 안 됨: {len(missing_jeonse)}개")

# 4. 매칭 안 된 그리드 상세
if len(missing_monthly) > 0:
    print(f"\n[월세 매칭 안 된 그리드 TOP 10]")
    for grid in sorted(list(missing_monthly))[:10]:
        count = df_monthly[df_monthly['grid_id'] == grid].shape[0]
        print(f"  - {grid}: {count}건")

if len(missing_jeonse) > 0:
    print(f"\n[전세 매칭 안 된 그리드 TOP 10]")
    for grid in sorted(list(missing_jeonse))[:10]:
        count = df_jeonse[df_jeonse['grid_id'] == grid].shape[0]
        print(f"  - {grid}: {count}건")

# 5. 병합 후 NaN 확인
df_merged_monthly = df_monthly.merge(
    df_mapping[['grid_id', 'district']], on='grid_id', how='left')
df_merged_jeonse = df_jeonse.merge(
    df_mapping[['grid_id', 'district']], on='grid_id', how='left')

nan_monthly = df_merged_monthly[df_merged_monthly['district'].isna()]
nan_jeonse = df_merged_jeonse[df_merged_jeonse['district'].isna()]

print(f"\n[병합 후 district가 NaN]")
print(
    f"  월세: {len(nan_monthly)}건 ({len(nan_monthly)/len(df_merged_monthly)*100:.1f}%)")
print(
    f"  전세: {len(nan_jeonse)}건 ({len(nan_jeonse)/len(df_merged_jeonse)*100:.1f}%)")

# 6. lat/lon 확인
if 'lat' in df_mapping.columns and 'lon' in df_mapping.columns:
    print(f"\n[좌표 정보]")
    print(
        f"  매핑 파일에 좌표 있음: {df_mapping[['lat', 'lon']].notna().all(axis=1).sum()}개")

    df_merged_monthly_full = df_monthly.merge(
        df_mapping[['grid_id', 'district', 'lat', 'lon']], on='grid_id', how='left')
    valid_coords_monthly = df_merged_monthly_full[[
        'lat', 'lon']].notna().all(axis=1).sum()

    df_merged_jeonse_full = df_jeonse.merge(
        df_mapping[['grid_id', 'district', 'lat', 'lon']], on='grid_id', how='left')
    valid_coords_jeonse = df_merged_jeonse_full[[
        'lat', 'lon']].notna().all(axis=1).sum()

    print(
        f"  월세 병합 후 좌표 있음: {valid_coords_monthly}건 ({valid_coords_monthly/len(df_merged_monthly_full)*100:.1f}%)")
    print(
        f"  전세 병합 후 좌표 있음: {valid_coords_jeonse}건 ({valid_coords_jeonse/len(df_merged_jeonse_full)*100:.1f}%)")

print("\n" + "="*70)
