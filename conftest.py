import pytest
import allure
import uuid

@pytest.fixture
def chrome_options(chrome_options):
    # chrome_options.binary_location = '/usr/bin/google-chrome-stable'
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--log-level=DEBUG')
    chrome_options.add_argument('--start-maximized')

    return chrome_options


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # Эта функция помогает обнаружить, что какой-то тест не пройден.
    # и передать эту информацию в разборку:

    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep


@pytest.fixture
def web_browser(request, selenium):

    browser = selenium

    # Вернуть экземпляр браузера в тестовый пример:
    yield browser

    # Сделать разрыв (этот код будет выполняться после каждого теста):

    if request.node.rep_call.failed:
        # Сделайте снимок экрана, если тест не пройден:
        try:
            browser.execute_script("document.body.bgColor = 'white';")

            # Сделать скриншот для локальной отладки:
            browser.save_screenshot('screenshots/' + str(uuid.uuid4()) + '.png')

            # Прикрепить скриншот к отчету Allure:
            allure.attach(browser.get_screenshot_as_png(),
                          name=request.function.__name__,
                          attachment_type=allure.attachment_type.PNG)

            # Для удачной отладки:
            print('URL: ', browser.current_url)
            print('Browser logs:')
            for log in browser.get_log('browser'):
                print(log)

        except:
            pass # просто игнорируйте любые ошибки здесь


def get_test_case_docstring(item):
    """ Эта функция получает строку документа из тестового примера и форматирует ее.
         чтобы отображать эту строку документации вместо имени тестового примера в отчетах.
    """

    full_name = ''

    if item._obj.__doc__:
        # Удалить лишние пробелы из строки документа:
        name = str(item._obj.__doc__.split('.')[0]).strip()
        full_name = ' '.join(name.split())

        # Сгенерировать список параметров для параметризованных тестовых случаев:
        if hasattr(item, 'callspec'):
            params = item.callspec.params

            res_keys = sorted([k for k in params])
            # Создать список на основе Dict:
            res = ['{0}_"{1}"'.format(k, params[k]) for k in res_keys]
            # Добавить dict со всеми параметрами к названию тестового примера:
            full_name += ' Parameters ' + str(', '.join(res))
            full_name = full_name.replace(':', '')

    return full_name


def pytest_itemcollected(item):
    """ Эта функция изменяет имена тестовых случаев «на лету»
    во время выполнения тестовых случаев.
    """

    if item._obj.__doc__:
        item._nodeid = get_test_case_docstring(item)


def pytest_collection_finish(session):
    """ Эта функция изменяет имена тестовых случаев «на лету»,
     когда мы используем параметр --collect-only для pytest
    (чтобы получить полный список всех существующих тестовых случаев).
    """

    if session.config.option.collectonly is True:
        for item in session.items:
            # Если в тестовом примере есть строка документа, нам нужно изменить ее имя на
            # это строка документа для отображения удобочитаемых отчетов и для
            # автоматически импортировать тестовые случаи в систему управления тестированием.
            if item._obj.__doc__:
                full_name = get_test_case_docstring(item)
                print(full_name)

        pytest.exit('Done!')
