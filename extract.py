from pdf2image import convert_from_path
import easyocr
import pandas as pd
import re
import os
import numpy as np

# Đường dẫn PDF
pdf_path = "a.pdf"

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"Không tìm thấy file PDF: {pdf_path}")

try:
    # Chuyển PDF -> ảnh
    pages = convert_from_path(pdf_path, dpi=300)
except Exception as e:
    print(f"Lỗi khi chuyển PDF sang ảnh: {e}")
    exit(1)

reader = easyocr.Reader(['vi'], gpu=False)

results = []
for i, page in enumerate(pages, start=1):
    try:
        # OCR toàn bộ text
        text = reader.readtext(np.array(page), detail=0, paragraph=True)
        text = "\n".join(text)
    except Exception as e:
        print(f"Lỗi OCR trang {i}: {e}")
        continue

    print(f"\n--- Nội dung OCR trang {i} ---")
    print(text)
    results.extend(text.split("\n"))

# Xử lý bảng từ OCR
data = []
for line in results:
    # Tách theo 2 hoặc nhiều khoảng trắng liên tiếp
    row = re.split(r"\s{2,}", line)
    # Loại bỏ dòng không đủ dữ liệu
    if len(row) > 1:
        data.append(row)

if data:
    # Nếu đoán được số cột, có thể đặt tên cột ở đây
    df = pd.DataFrame(data)
    print(df.head(10))
else:
    print("Không tìm thấy dữ liệu bảng phù hợp.")