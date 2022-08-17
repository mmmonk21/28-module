# этот тест выполняется первым для того, чтобы получить куки и записать их в файл
# для запуска теста нужно выполнит команду:
# python -m pytest -v --driver Chrome --driver-path C:\ChromeDriveSelenium\chromedriver.exe tests\test_authorisation.py
from pages.auth_page import AuthPage
from tests.data import correct_email,correct_pass
import pickle

def test_authorisation_with_correct_data(web_browser):
    """при вводе в поля формы авторизации корректных данных действующего пользователя происходит вход в аккаунт"""
    page = AuthPage(web_browser)
    page.email_field.send_keys(correct_email)
    page.pass_field.send_keys(correct_pass)
    page.login_button.click()
    assert page.get_relative_link()=='/member/','При вводе в поля формы авторизации корректных данных действующего пользователя не происходит вход в аккаунт'
    # сохраняем куки в файл
    with open('cookies.tmp', 'wb') as cookies:
        pickle.dump(web_browser.get_cookies(), cookies)
