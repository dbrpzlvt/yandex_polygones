import msvcrt
import json
from time import sleep
from scraper.browser import get_driver
from scraper.yandex_maps import inject_custom_js, setup_listener, wait_for_polygons, click_on_city
from scraper.to_geojson import json_to_geojson
from tqdm import tqdm
import pandas as pd



# class YandexPolygones():
#     def __init__(self):
#         pass
def parse_polygones(df_pop, chunk, n):
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

        result = click_on_city(driver, df_pop.loc[i, 'search'])  # result это и есть isdone

        # print("Перейди вручную на нужный населённый пункт и кликни по нему, чтобы получить полигоны")
        
        polygons_data = wait_for_polygons(driver, timeout=30)
        
        df_pop.at[i, 'isdone'] = result
        # df_pop.at[i, 'URL'] = URL
        # df_pop.at[i, 'lat'] = lat
        # df_pop.at[i, 'lon'] = lon        

        # print(f"{polygons_data}, {result}, {URL}, {lat}, {lon}")

        if result == 2:
            # df_pop.at[i, 'isdone'] = result
            print("Перезагружаю браузер...")
            driver.refresh()
            driver.get(yandex_url)
            # sleep(5)
            continue

        if polygons_data:
            print("Получены данные:")
            print(polygons_data)
            json_all.append(polygons_data)
            # Сохрани или обработай дальше
            # n += 1
        else:
            print("Данные не получены за время ожидания")


    print(f"Получено полигонов: {len(polygons_data)}")
    with open(f"{path_se}" + "data.json", "w", encoding='utf-8') as file:
        json.dump(json_all, file, indent=4)
    
    print("Нажмите любую клавишу, чтобы продолжить...")
    msvcrt.getch()

    with open(f"{path_se}" + "data.json", 'r', encoding='utf-8') as f:
        data = json.load(f)  # прочитали
    json_to_geojson(data)  # сохранили

    print("Нажмите любую клавишу еще раз, чтобы закончить...")
    msvcrt.getch()

    driver.quit()

if __name__ == '__main__':
    path_se = r".\\out\\"
    path = r".\\raw_data\\addresses_Prim_kraj.xlsx"
    n = 0
    chunk_size = 10
    json_all = []
    if path.endswith(".xls") or path.endswith(".xlsx"):
        print(f'Обрабатываю файл: {path} ...')
        temp_df = pd.read_excel(path)
        while n < len(temp_df[temp_df['isdone'] == 0]):
            parse_polygones(temp_df, chunk_size, n)
            temp_df.to_excel(path_se + 'file_with_isdone.xlsx', index=False)
        print("Все обработано")
