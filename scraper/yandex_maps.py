import time
import numpy as np

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
    ВАЖНО! Реализация зависит от структуры исходного кода HTML и может потребовать доработки.
    Чаще всего меняются только XPATH и CSS_SELECTOR'ы
    """

    search_input_xpath = "//input[@placeholder='Поиск и выбор мест']"

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, \
    ElementNotInteractableException, SessionNotCreatedException, NoSuchWindowException

    wait = WebDriverWait(driver, np.random.randint(20, 30))

    try:
        adr_txt = city_name
        adr_elem = wait.until(
            EC.visibility_of_element_located((By.XPATH, search_input_xpath)))
        
        adr_elem.send_keys(Keys.CONTROL + "a")
        adr_elem.send_keys(Keys.BACKSPACE)
        adr_elem.send_keys(adr_txt)
        # div_element = driver.find_element(By.CSS_SELECTOR, 'div.search-snippet-view__body._type_business')
        # ActionChains(driver).context_click(div_element).perform()
        time.sleep(1) # жду секунду, чтобы загрузился выпадающий список, откуда я возьму первое значение
        # adr_elem.send_keys(Keys.DOWN)
        # time.sleep(1)
        try:
            # ищу элемент с атрибутом aria-activedescendant='0:0' из выпадающего списка, когда вводится адрес
            # если нужно выбрать другой (второй, третий и так далее) элемент, измените значение '0:0' на нужное
            # builder.moveToElement(someElement).build().perform();
            # element_to_click = wait.until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-activedescendant='0:0']"))
            # )
            
            adr_elem.send_keys(Keys.ENTER)
            time.sleep(1)
            # adr_elem.click()
            # element_to_click.click()
            # Щелчок левой кнопкой мыши по элементу (ЛКМ)
            # webdriver.ActionChains(driver).context_click(element_to_click).perform()

        except Exception as e:
            assert Warning("Не удалось найти элемент для клика:", e)
            return 2

        # URL = driver.current_url  # совсем забыл, еще нужна URL'ка, надеюсь найду способ как ее дальше воткнуть
        # coords = wait.until(EC.visibility_of_element_located(
        #             (By.XPATH, "//div[contains(@class, 'toponym-card-title-view__coords-badge')]")))
        # lat, lon = [eval(x) for x in coords.text.split(', ')]
        return 1
    except(TimeoutException, NoSuchElementException, StaleElementReferenceException,
                ElementNotInteractableException, SessionNotCreatedException,
                ValueError, IndexError) as e:
        return 2

def inject_custom_js(driver):
    # Сначала вставляем custom.js код напрямую (чтобы fetch перехватить)
    with open('scraper/custom.js', 'r', encoding='utf-8') as f:
        custom_js = f.read()
    driver.execute_script(custom_js)

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