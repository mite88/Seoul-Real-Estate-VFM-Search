# fix_duplicate_grids.py
"""
중복된 grid_id를 제거하고 각 그리드당 하나의 대표 좌표만 남김
(지도 시각화용 매핑 파일 생성)
"""

import pandas as pd
from pathlib import Path

print("=" * 60)
print("중복 grid_id 제거 (지도 시각화용)")
print("=" * 60)

# 매핑 파일 로드
mapping_path = Path('data/grid_district_mapping.csv')
df_mapping = pd.read_csv(mapping_path)

print(f"\n원본 데이터:")
print(f"  총 행 수: {len(df_mapping):,}")
print(f"  고유 grid_id 수: {df_mapping['grid_id'].nunique():,}")

# 컬럼명 확인 및 표준화
if 'latitude' in df_mapping.columns and 'longitude' in df_mapping.columns:
    df_mapping = df_mapping.rename(
        columns={'latitude': 'lat', 'longitude': 'lon'})
    print(f"  컬럼명 변경: latitude → lat, longitude → lon")

# 중복 확인
duplicates = df_mapping[df_mapping.duplicated(subset=['grid_id'], keep=False)]
print(f"  중복된 행 수: {len(duplicates):,}")

# 각 grid_id의 평균 좌표 사용 (격자의 중심점)
print(f"\n각 grid_id의 대표 좌표 계산 중...")
df_unique = df_mapping.groupby('grid_id').agg({
    'lat': 'mean',        # 평균 위도
    'lon': 'mean',        # 평균 경도
    # 가장 많이 나타나는 구
    'district': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]
}).reset_index()

print(f"\n중복 제거 후:")
print(f"  총 행 수: {len(df_unique):,}")
print(f"  고유 grid_id 수: {df_unique['grid_id'].nunique():,}")

# 매핑 통계
print(f"\n매핑 통계:")
mapped_count = df_unique['district'].notna().sum()
unmapped_count = df_unique['district'].isna().sum()
print(f"  ✅ 매핑 성공: {mapped_count:,}개 ({mapped_count/len(df_unique)*100:.1f}%)")
print(
    f"  ❌ 매핑 실패: {unmapped_count:,}개 ({unmapped_count/len(df_unique)*100:.1f}%)")

if mapped_count > 0:
    print(f"\n  구별 분포:")
    district_counts = df_unique['district'].value_counts()
    for district, count in district_counts.head(10).items():
        print(f"    • {district}: {count}개 ({count/mapped_count*100:.1f}%)")

# GRID_02028 확인
print(f"\n특정 그리드 확인:")
grid_02028 = df_unique[df_unique['grid_id'] == 'GRID_02028']
if not grid_02028.empty:
    row = grid_02028.iloc[0]
    print(f"\n  GRID_02028 (중복 제거 후):")
    print(f"    좌표: (lat={row['lat']:.6f}, lon={row['lon']:.6f})")
    print(f"    구: {row['district']}")

# 저장
output_path = Path('data/grid_district_mapping.csv')
df_unique.to_csv(output_path, index=False, encoding='utf-8-sig')

file_size_kb = output_path.stat().st_size / 1024
print(f"\n💾 저장 완료:")
print(f"   파일: {output_path}")
print(f"   크기: {file_size_kb:.1f} KB")
print(f"   행 수: {len(df_unique):,}")
print(f"   컬럼: {df_unique.columns.tolist()}")

# 샘플 데이터 출력
print(f"\n📋 샘플 데이터 (처음 10개):")
print(df_unique.head(10).to_string(index=False))

print("\n" + "=" * 60)
print("✅ 중복 제거 완료!")
print("=" * 60)
print("\n다음 명령으로 앱을 실행하세요:")
print("  streamlit run app.py")
print("\n" + "=" * 60)
