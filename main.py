# from scraper.browser import get_driver
# from scraper.yandex_maps import click_on_city, get_polygons_from_map
# from utils.file_helpers import save_json

# def main():
#     driver = get_driver(headless=False)
#     driver.get('https://yandex.ru/maps/')

#     city_name = "Великий Новгород"
#     click_on_city(driver, city_name)

#     polygons = get_polygons_from_map(driver)
#     if isinstance(polygons, dict) and 'error' in polygons:
#         print("Ошибка при получении полигонов:", polygons['error'])
#     else:
#         print(f"Получено полигонов: {len(polygons)}")
#         save_json(polygons, 'data/polygons.json')

#     driver.quit()

import msvcrt
import json
from scraper.browser import get_driver
from scraper.yandex_maps import inject_custom_js, setup_listener, wait_for_polygons

def main():
    driver = get_driver(headless=False)
    driver.get('https://yandex.ru/maps/')

    n = 0
    json_all = []
    while n < 5:
        inject_custom_js(driver)    # Вставляем custom.js, который перехватывает fetch
        setup_listener(driver)      # Подписываемся на событие FromPage

        print("Перейди вручную на нужный населённый пункт и кликни по нему, чтобы получить полигоны")

        polygons_data = wait_for_polygons(driver, timeout=60)

        if polygons_data:
            print("Получены данные:")
            print(polygons_data)
            json_all.append(polygons_data)
            # Сохрани или обработай дальше
            n += 1
        else:
            print("Данные не получены за время ожидания")
    # json_all = {json_all}
    print("Нажмите любую клавишу, чтобы закончить...")
    with open("./data/data.json", "w") as file:
        json.dump(json_all, file, indent=4)
    msvcrt.getch()
    driver.quit()

if __name__ == '__main__':
    main()