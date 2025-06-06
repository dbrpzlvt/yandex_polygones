import time

def get_polygons_from_map(driver):
    # Загружаем JS код из файла
    with open('scraper/js_scripts.js', 'r', encoding='utf-8') as f:
        js_code = f.read()

    # Выполняем JS код на странице
    result = driver.execute_script(js_code)
    return result

def click_on_city(driver, city_name):
    """
    Пример функции, которая ищет и кликает по населенному пункту.
    Реализация зависит от структуры DOM и может потребовать доработки.
    """
    # Пример: поиск поля поиска и ввод названия города
    search_input_xpath = "//input[@placeholder='Поиск и выбор мест']"
    search_button_xpath = "//button[contains(@class, 'button _view_search _size_medium')]"

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 10)

    # Находим поле поиска
    search_input = wait.until(EC.presence_of_element_located((By.XPATH, search_input_xpath)))
    search_input.clear()
    search_input.send_keys(city_name)

    # Нажимаем кнопку поиска
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, search_button_xpath)))
    search_button.click()

    # # Ждем загрузки результатов и кликаем по первому результату
    # time.sleep(5)  # Можно заменить на более умное ожидание

    # # Клик по первому результату (пример)
    # first_result_xpath = "(//div[contains(@class, 'search-snippet-view')])[1]"
    # first_result = wait.until(EC.element_to_be_clickable((By.XPATH, first_result_xpath)))
    # first_result.click()

    time.sleep(5)  # Ждем отрисовки полигонов

def inject_custom_js(driver):
    # Сначала вставляем custom.js код напрямую (чтобы fetch перехватить)
    with open('scraper/custom.js', 'r', encoding='utf-8') as f:
        custom_js = f.read()
    driver.execute_script(custom_js)

def inject_inject_js(driver):
    # inject.js ссылается на custom.js как внешний скрипт, но у нас нет расширения chrome,
    # поэтому перепишем inject.js так, чтобы он просто вызывал custom.js код напрямую.
    # Здесь можно упростить, например, пропустить inject.js и вставить custom.js напрямую.
    pass  # Можно оставить пустым или использовать для других целей

def setup_listener(driver):
    # Подписываемся на событие FromPage и сохраняем данные в window.lastPolygonData
    setup_listener_js = """
    window.lastPolygonData = null;
    window.addEventListener('FromPage', function(e) {
        window.lastPolygonData = e.detail;
        console.log('FromPage event caught', e.detail);
    });
    """
    driver.execute_script(setup_listener_js)

def wait_for_polygons(driver, timeout=100):
    start = time.time()
    while time.time() - start < timeout:
        data = driver.execute_script("return window.lastPolygonData;")
        if data:
            return data
        time.sleep(0.5)
    return None