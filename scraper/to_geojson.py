import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
import json

# def list_depth(self, list_of_lists):
#     if isinstance(list_of_lists, list):
#         if len(list_of_lists) == 0:
#             depth = 1
#         else:
#             depth = 1 + max([self.list_depth(l) for l in list_of_lists])
#     else:
#         depth = 0
#     return depth



def json_to_geojson(data, file_name):
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

    # Обработка каждого объекта в массиве JSON
    for item in data:
        name = item['name']
        address = item['address']
        description = item['description']
        polygons = item['polygons']
        multi_polygons = []  # объект для мультиполигона

        # Преобразование полигонов в Shapely объекты
        try:
            if len(polygons) > 1:  # если количество полигонов для одного объекта больше один создаем объект MultiPolygon
                for polygon in polygons:
                    # for coords in polygon:  # Создание полигонов из координат
                    geom = Polygon(polygon) if len(polygon) > 2 else None   # если полигон состоит из одной или двух точек - инвалид
                    multi_polygons.append(geom)
                geom = MultiPolygon(multi_polygons)
            else:
                polygon = polygons[0]  # внутри атрибута полигонов (item['polygons']) только один элемент - сам полигон
                # так как структура этого атрибута всегда состоит из списка списков максимум до 3-го уровня. 
                # сначала думал, что надо находить глубину вложенности item['polygons']: если равна 3 - мульти, если 2 - обычный, но нет...
                # for coords in polygons:  # Создание полигонов из координат
                geom = Polygon(polygon) if len(polygon) > 2 else None
        except:
            raise Warning(f"Геометрия для региона {address} неверная.\nПроверьте ее вручную, либо пропустите")
        # и добавляем в наш полученный объект все остальные атрибуты 'item' из JSON, если геометрия получилась верная
        if geom:
            geometries.append(geom)
            names.append(name)
            addresses.append(address)
            descriptions.append(description)
        else:
            raise Warning("Геометрия неверная")

    # Создание GeoDataFrame
    gdf = gpd.GeoDataFrame({'name': names, 
                            'address': addresses, 
                            'description': descriptions, 
                            'geometry': geometries})
    gdf.crs = "EPSG:4326"

    # Сохранение в GeoJSON
    gdf.to_file(r'.\\out\\'+file_name.replace(".json", ".geojson"), driver='GeoJSON')