import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
import json

def json_to_geojson(data):
# Загрузка вашего JSON файла
    # with open(r'.\\out\\data.json', 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    if data is None:
        raise Warning("Ошибка в файле .json")
    # Создание списка для хранения геометрий и атрибутов
    geometries = []
    names = []
    addresses = []
    descriptions = []

    # Обработка каждого объекта в массиве
    for item in data:
        name = item['name']
        address = item['address']
        description = item['description']
        polygons = item['polygons']
        
        # Преобразование полигонов в Shapely объекты
        for polygon in polygons:
            # Создание полигонов из координат
            geom = Polygon(polygon) if len(polygon) > 2 else None
            if geom:
                geometries.append(geom)
                names.append(name)
                addresses.append(address)
                descriptions.append(description)

    # Создание GeoDataFrame
    gdf = gpd.GeoDataFrame({'name': names, 
                            'address': addresses, 
                            'description': descriptions, 
                            'geometry': geometries})

    # Сохранение в GeoJSON
    gdf.to_file(r'.\\out\\geo_data.geojson', driver='GeoJSON')