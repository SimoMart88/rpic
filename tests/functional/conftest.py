import pytest


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

    return chrome_options
