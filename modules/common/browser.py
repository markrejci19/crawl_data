from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth
import geckodriver_autoinstaller

def init_driver():
    # Tự động cài geckodriver nếu chưa có
    geckodriver_autoinstaller.install()
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    # Áp dụng selenium-stealth để giả lập trình duyệt thật (nếu hỗ trợ)
    try:
        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
    except Exception:
        pass  # Firefox có thể không hỗ trợ hết các tuỳ chọn này, nhưng không ảnh hưởng crawl
    wait = WebDriverWait(driver, 10)
    return driver, wait