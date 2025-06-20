import os
import json
from time import sleep
from scraper.browser import get_driver
from scraper.yandex_maps import inject_custom_js, setup_listener, wait_for_polygons, click_on_city
from scraper.to_geojson import json_to_geojson
from tqdm import tqdm
import pandas as pd
# from collections import OrderedDict



class YandexPolygones:
    def parse_polygones(json_all, df_pop, chunk, n):
        yandex_url = 'https://yandex.ru/maps/'
        driver = get_driver(headless=False)
        driver.get(yandex_url)

        # ждем 2 секунды, чтобы страница прогрузилась
        sleep(2)

        # фильтруем то, что нам надо обрабатывать в данный момент: isdone == 0,  адрес - не пустой,
        # срез - от текущего n до конца чанка
        idx_seek = df_pop[(df_pop['isdone'] == 0) & ~df_pop['search'].isnull()].iloc[n:n + chunk].copy()

        # n = 0
        
        for i in tqdm(idx_seek.index):

            inject_custom_js(driver)    # Вставляем custom.js, который перехватывает fetch
            setup_listener(driver)      # Подписываемся на событие FromPage

            click_on_city(driver, df_pop.loc[i, 'search'])  # раньше было эта функция возвращала result который и есть isdone

            # print("Перейди вручную на нужный населённый пункт и кликни по нему, чтобы получить полигоны")
            
            result, polygons_data = wait_for_polygons(driver, timeout=30)
            
            df_pop.at[i, 'isdone'] = result

            # print(f"{polygons_data}, {result}, {URL}, {lat}, {lon}")

            if result == 2:
                print(f"Данные по '{df_pop.loc[i, 'search']}' не получены за время ожидания...")
                print("Перезагружаю браузер...")

                driver.refresh()
                driver.get(yandex_url)

                assert Warning(f"Данные не получены за время ожидания :(\nПерехожу к следующему адресу")
                continue

            if polygons_data:
                print("Получены данные:")
                print(polygons_data)
                # df_pop.at[i, 'URL'] = URL  # ЮЭРЕЛЬКУ никак не собрать, ее нету в JSON'е, поэтому обойдемся как-нибудь
                df_pop.at[i, 'lat'] = polygons_data['centroid'][1]
                df_pop.at[i, 'lon'] = polygons_data['centroid'][0]
                df_pop.at[i, 'short_Yandex_address'] = polygons_data['description']
                df_pop.at[i, 'yandex_address'] = polygons_data['address']
                json_all.append(polygons_data)
                # n += 1

        # если такой файл уже существует
        if os.path.exists(str(path['out']+json_file_name)):
            with open(f"{path['out']}" + json_file_name, "r+", encoding='utf-8') as file:
                if os.path.getsize(f"{path['out']}" + json_file_name) != 0:
                    try:
                        file.seek(0) # переместили каретку в начало файла
                        exist_data = json.load(file)  # прочитали то, что есть внутри
                        json_all.extend(exist_data)  # РАСШИРИЛИ то, что было (append - плохо а-та-та)
                        set_of_jsons = {json.dumps(d, sort_keys=True) for d in json_all}  # убираю дубликаты объектов JSON, после слияния - целых, я так понимаю побитово
                        json_all = [json.loads(t) for t in set_of_jsons]  # сохраняю обратно
                        
                    except json.decoder.JSONDecodeError as e:
                        raise Warning(f"Файл JSON '{file.name}' пуст или сломался и содержит инвалидные данные :(\n"
                                    f"Более подробная информация тут: {e}")
                    
                file.seek(0) # переместили каретку в начало файла

                print(f"Получено полигонов: {len(json_all)}")
                # json_all = list(set(json_all))
                json.dump(json_all, file, indent=4, ensure_ascii=False)  # сохранили, indent - отступ при печати в файл, чтобы было красиво
                
                json_to_geojson(json_all, json_file_name)  # сохранили ГЕО-джейсон
                file.close()
        else:  # а если нет......
            with open(f"{path['out']}" + json_file_name, "w", encoding='utf-8') as file:
                file.seek(0) # переместили каретку в начало файла

                print(f"Получено полигонов: {len(json_all)}")
                # json_all = list(set(json_all))
                json.dump(json_all, file, indent=4, ensure_ascii=False)  # сохранили, indent - отступ при печати в файл, чтобы было красиво
                
                json_to_geojson(json_all, json_file_name)  # сохранили ГЕО-джейсон
                file.close()

        # print("Нажмите любую клавишу, чтобы продолжить...")
        # msvcrt.getch()

        # with open(f"{path['out']}" + "data.json", 'r', encoding='utf-8') as file:
        #     data = json.load(file)  # прочитали
        # json_to_geojson(data)  # сохранили

        # print("Нажмите любую клавишу еще раз, чтобы закончить...")
        # msvcrt.getch()

        driver.quit()

if __name__ == '__main__':

    path = {"out": r".\\out\\",
            "raw_data": r".\\raw_data\\"
            }
    excel_file_name = "СНТ_ЛО.xlsx"
    json_file_name = "СНТ_ЛО.json"
    # path = r".\\raw_data\\addresses_Prim_kraj.xlsx"

    json_all = []
    n = 0
    chunk_size = 10

    if str(path["raw_data"]+excel_file_name).endswith(".xls") or str(path["raw_data"]+excel_file_name).endswith(".xlsx"):
        print(f'Обрабатываю файл: {path["raw_data"]+excel_file_name} ...')
        temp_df = pd.read_excel(path["raw_data"]+excel_file_name)
        while n < len(temp_df[temp_df['isdone'] == 0]):
            YandexPolygones.parse_polygones(json_all, temp_df, chunk_size, n)
            temp_df.to_excel(path["raw_data"] + excel_file_name, index=False)
        print("Все обработано!")
