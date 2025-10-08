import time
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


URL = "https://techcombank.com/cong-cu-tien-ich/bieu-phi-lai-suat"
XPATH_TO_CLICK = "/html/body/div[1]/div/div[2]/div/div/div[4]/div/div/div/div/div/section/div/div[2]/div[1]/div[2]/div/p[2]"
LINK_TEXT = "Biểu lãi suất huy động Techcombank cho Khách hàng doanh nghiệp"
DOWNLOAD_DIR = Path(__file__).resolve().parent / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _wait_for_download_complete(dir_path: Path, timeout: int = 120) -> Optional[Path]:
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(1.0)
        files = list(dir_path.glob("*"))
        if any(f.suffix in {".crdownload", ".tmp", ".part"} for f in files):
            continue
        if files:
            latest = max(files, key=lambda p: p.stat().st_mtime)
            return latest
    return None

def build_driver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    prefs = {
        "download.default_directory": str(DOWNLOAD_DIR),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(DOWNLOAD_DIR)
        })
    except Exception:
        pass
    driver.set_page_load_timeout(120)
    return driver


def _find_href_from_rows(driver: webdriver.Chrome) -> Optional[tuple[Optional[object], str]]:
    rows = driver.find_elements(By.CSS_SELECTOR, "div.row")
    for row in rows:
        try:
            content_h4 = row.find_element(By.CSS_SELECTOR, "div.content h4.text-base.font-semibold")
            if (content_h4.text or "").strip() == LINK_TEXT:
                anchors = row.find_elements(By.CSS_SELECTOR, "div.file-download .show-document a")
                for a in anchors:
                    href = (a.get_attribute("href") or "").strip()
                    if href:
                        return a, href
                anchors_any = row.find_elements(By.CSS_SELECTOR, "div.file-download a")
                for a in anchors_any:
                    href = (a.get_attribute("href") or "").strip()
                    if href:
                        return a, href
        except Exception:
            continue
    return None
def main():
    driver = build_driver()
    wait = WebDriverWait(driver, 40)
    try:
        driver.get(URL)

        try:
            btn = driver.find_element(By.XPATH, "//button[contains(., 'Chấp nhận') or contains(., 'Đồng ý') or contains(., 'Accept')]")
            btn.click()
        except Exception:
            pass
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, XPATH_TO_CLICK)))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
        time.sleep(0.5)
        elem.click()
        anchor_and_href = _find_href_from_rows(driver)
        href_for_download: str = ""
        download_link = None
        if anchor_and_href:
            download_link, href_for_download = anchor_and_href
        else:
            try:
                tab = driver.find_element(By.XPATH, "//p[@id='lai-suat-khdn' and contains(@class,'tcb-tabs_item')]")
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tab)
                time.sleep(0.3)
                tab.click()
                time.sleep(0.8)
                anchor_and_href = _find_href_from_rows(driver)
                if anchor_and_href:
                    download_link, href_for_download = anchor_and_href
            except Exception:
                pass

        if not download_link and not href_for_download:
            raise TimeoutError("Không tìm thấy link cần tải.")

        before_files = set(DOWNLOAD_DIR.glob("*"))
        clicked = False
        if download_link is not None:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", download_link)
                time.sleep(0.3)
                download_link.click()
                clicked = True
            except Exception:
                clicked = False
            if not href_for_download:
                try:
                    href_for_download = download_link.get_attribute("href") or ""
                except Exception:
                    href_for_download = href_for_download or ""

        if not clicked and href_for_download:
            driver.get(href_for_download)
            time.sleep(1.0)

        file_path = _wait_for_download_complete(DOWNLOAD_DIR, timeout=180)
        if (not file_path) or (file_path in before_files):
            if href_for_download:
                driver.get(href_for_download)
                file_path = _wait_for_download_complete(DOWNLOAD_DIR, timeout=60)
        if not file_path or file_path in before_files:
            raise RuntimeError("Không tải được file.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()