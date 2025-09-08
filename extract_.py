import sys
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from pathlib import Path
from datetime import datetime
import time
from modules.common.browser import init_driver

def run():
    driver, wait = init_driver()
    URL = "https://vn.investing.com/economic-calendar/gdp-375"
    driver.get(URL)
    time.sleep(2)

    # Lặp cho đến khi nút "Xem thêm" không còn xuất hiện
    show_more_xpath = '//*[@id="showMoreHistory375"]'
    retry = 0
    max_retry = 10
    while retry < max_retry:
        try:
            # Chờ nút xuất hiện (timeout ngắn)
            show_more_btn = wait.until(
                EC.presence_of_element_located((By.XPATH, show_more_xpath))
            )
            # Nếu hiển thị popup, gửi ESC để đóng
            try:
                driver.switch_to.active_element.send_keys(Keys.ESCAPE)
                time.sleep(0.5)
            except Exception:
                pass
            # Scroll đến nút (phòng trường hợp bị che)
            driver.execute_script("arguments[0].scrollIntoView(true);", show_more_btn)
            time.sleep(0.5)
            # Click nút
            show_more_btn.click()
            time.sleep(1.2)
        except Exception:
            # Không còn nút hoặc hết lần thử
            break
        retry += 1

    # Đợi bảng dữ liệu đầy đủ (có thể tăng thời gian nếu mạng chậm)
    time.sleep(2)
    table_xpath = '//*[@id="eventHistoryTable375"]'
    table_element = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
    table_html = table_element.get_attribute('outerHTML')
    driver.quit()

    # Ghi ra file HTML đầy đủ
    full_html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Bảng dữ liệu GDP Investing.com</title>
    </head>
    <body>
        <h1>Bảng dữ liệu GDP - Investing.com</h1>
        {table_html}
    </body>
    </html>
    """
    current_folder = Path(__file__).resolve().parent.name
    output_dir = Path(__file__).resolve().parents[3] / 'CRAW_HTML' / current_folder
    output_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.today().strftime('%Y%m%d')
    output_file = output_dir / f'gdp_investing_{today_str}.html'
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_html)
    return URL

if __name__ == "__main__":
    run()