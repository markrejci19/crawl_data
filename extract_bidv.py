import requests
from lxml import html

# URL cần lấy dữ liệu
url = "https://bidv.com.vn/vn/ca-nhan/cong-cu-tien-ich/lai-suat"

# Gửi yêu cầu GET tới trang web
response = requests.get(url)
response.encoding = 'utf-8'  # Đảm bảo đúng encoding tiếng Việt

# Phân tích HTML
tree = html.fromstring(response.text)

# XPath của bảng cần lấy
xpath = '//*[@id="pills-traculaisuat"]/section[2]/div/div/div[1]/table'

# Trích xuất bảng
table = tree.xpath(xpath)

if table:
    # Lấy tất cả các dòng trong bảng
    rows = table[0].xpath(".//tr")
    for row in rows:
        # Lấy dữ liệu từng ô (cell) trong dòng
        cells = row.xpath(".//th|.//td")
        data = [cell.text_content().strip() for cell in cells]
        print(data)
else:
    print("Không tìm thấy bảng với XPath đã cung cấp.")