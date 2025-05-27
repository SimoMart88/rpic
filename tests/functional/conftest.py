import pytest
import typing
from django.urls import reverse

from test_utils.selenium import selenium_login_as

if typing.TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from pytest_django.live_server_helper import LiveServer
    from django.contrib.auth.models import User

@pytest.fixture
def chrome_options(request, chrome_options):
    if not request.config.getvalue('show_browser'):
        chrome_options.add_argument('--headless')

    chrome_options.add_argument('--allow-insecure-localhost')
    chrome_options.add_argument('--disable-browser-side-navigation')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--guest')

    return chrome_options


@pytest.fixture
def selenium_logged_admin(selenium: "WebDriver", live_server: "LiveServer", admin_user: "User") -> "WebDriver":
    return selenium_login_as(selenium, live_server, admin_user, reverse('admin:login'))
