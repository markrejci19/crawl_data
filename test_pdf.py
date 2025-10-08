import requests
import pdfplumber

# Tải file PDF
# url = "https://media.eximbank.com.vn/exim/files/TB%20LSHD%20VND%20KHBL%20hieu%20luc%2031072025_Website.pdf"
# pdf_path = "downloaded.pdf"
# response = requests.get(url)
# with open(pdf_path, "wb") as f:
#     f.write(response.content)

# # Đọc dữ liệu tiếng Việt từ file PDF
# with pdfplumber.open(pdf_path) as pdf:
#     for page in pdf.pages:
#         text = page.extract_text()
#         print(text)

# Trích xuất bảng từ file PDF Eximbank
# Nếu muốn lấy bảng, dùng extract_tables()
# url = "https://media.eximbank.com.vn/exim/files/TB%20LSHD%20VND%20KHBL%20hieu%20luc%2031072025_Website.pdf"
# pdf_path = "downloaded.pdf"
# # response = requests.get(url)
# # with open(pdf_path, "wb") as f:
# #     f.write(response.content)
# try:
#     with pdfplumber.open(pdf_path) as pdf:
#         for i, page in enumerate(pdf.pages):
#             tables = page.extract_tables()
#             for t_idx, table in enumerate(tables):
#                 print(f"Eximbank - Page {i+1} - Table {t_idx+1}:")
#                 for row in table:
#                     print(row)
#                 print()
# except Exception as e:
#     print(f"Không thể đọc bảng từ file Eximbank: {e}")

# # Tải file PDF Sacombank
# url2 = "https://www.sacombank.com.vn/content/dam/sacombank/files/cong-cu/lai-suat/tien-gui/khcn/SACOMBANK_LAISUATNIEMYETTAIQUAY_KHCN_VIE.pdf"
# pdf_path2 = "sacombank.pdf"
# response2 = requests.get(url2)
# with open(pdf_path2, "wb") as f:
#     f.write(response2.content)

# # Đọc dữ liệu tiếng Việt từ file PDF Sacombank
# with pdfplumber.open(pdf_path2) as pdf:
#     for page in pdf.pages:
#         tables = page.extract_tables()
#         for t_idx, table in enumerate(tables):
#             print(f"Sacombank - Table {t_idx+1}:")
#             for row in table:
#                 print(row)
#             print()

# Tải file PDF HDBank
# url3 = "https://cdn.hdbank.com.vn/hdbank-file/document/20250611BIEULAISUATTIENGUIKHACHHANGCANHANKHCNWEBSITE_1749560757691.pdf"
# pdf_path3 = "hdbank.pdf"
# response3 = requests.get(url3)
# with open(pdf_path3, "wb") as f:
#     f.write(response3.content)

# # Đọc và trích xuất bảng từ file PDF HDBank
# with pdfplumber.open(pdf_path3) as pdf:
#     for i, page in enumerate(pdf.pages):
#         tables = page.extract_tables()
#         for t_idx, table in enumerate(tables):
#             print(f"HDBank - Page {i+1} - Table {t_idx+1}:")
#             for row in table:
#                 print(row)
#             print()

# Tải file PDF Techcombank
url4 = "https://techcombank.com/content/dam/techcombank/public-site/documents/bieu-lai-suat-huy-dong-techcombank-cho-khach-hang-doanh-nghiep-cap-nhat-14apr.pdf"
pdf_path4 = "techcombank.pdf"
response4 = requests.get(url4)
with open(pdf_path4, "wb") as f:
    f.write(response4.content)

# Đọc và trích xuất bảng từ file PDF Techcombank
with pdfplumber.open(pdf_path4) as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for t_idx, table in enumerate(tables):
            print(f"Techcombank - Page {i+1} - Table {t_idx+1}:")
            for row in table:
                print(row)
            print()

# Lấy bảng lãi suất từ trang BIDV và lưu ra file HTML
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path
import time
from modules.common.browser import init_driver_dldir

url_bidv = "https://bidv.com.vn/vn/ca-nhan/cong-cu-tien-ich/lai-suat"

# Sử dụng selenium để lấy bảng lãi suất BIDV
output_dir = Path('.')
today = datetime.today().strftime('%Y%m%d')
output_file = output_dir / f"bidv_khcn_{today}.html"
driver, wait = init_driver_dldir(download_dir=str(output_dir))
driver.get(url_bidv)
try:
    # Chờ bảng xuất hiện
    table_elem = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="pills-traculaisuat"]/section[2]/div/div/div[1]/table'))
    )
    html_table = table_elem.get_attribute('outerHTML')
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_table)
    print(f"Đã lưu bảng BIDV vào {output_file}")
except Exception as e:
    print(f"Không tìm thấy bảng lãi suất trên trang BIDV: {e}")
finally:
    driver.quit()
