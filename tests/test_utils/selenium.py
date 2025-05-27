import typing
from selenium.webdriver.common.by import By


if typing.TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from pytest_django.live_server_helper import LiveServer
    from django.contrib.auth.models import User


def selenium_login_as(selenium: "WebDriver", live_server: "LiveServer", user: "User",
                      login_url: str):
    selenium.get(f"{live_server.url}{login_url}")
    username_field = selenium.find_element(By.CSS_SELECTOR, 'form input[name="username"]')
    password_field = selenium.find_element(By.CSS_SELECTOR,'form input[name="password"]')
    username_field.send_keys(user.username)
    password_field.send_keys("password")
    submit = selenium.find_element(By.CSS_SELECTOR,'form input[type="submit"]')
    submit.click()
    return selenium
