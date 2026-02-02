# modules/geo_utils.py
import json
from shapely.geometry import Point, shape


class SeoulDistrictMapper:
    def __init__(self, geojson_path='data/seoul_districts.json'):
        with open(geojson_path, 'r', encoding='utf-8') as f:
            self.geojson = json.load(f)

        # 구 경계 폴리곤 생성
        self.districts = {}
        for feature in self.geojson['features']:
            name = feature['properties']['name']
            polygon = shape(feature['geometry'])
            self.districts[name] = polygon

    def get_district(self, lat, lon):
        """좌표로 구 찾기"""
        point = Point(lon, lat)  # 주의: (lon, lat) 순서

        for name, polygon in self.districts.items():
            if polygon.contains(point):
                return name

        return None


# 사용 예시
mapper = SeoulDistrictMapper()
district = mapper.get_district(37.5460, 127.1620)
print(district)  # 강동구
