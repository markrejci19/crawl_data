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
        # Lấy kết quả OCR chi tiết
        ocr_result = reader.readtext(np.array(page), detail=1, paragraph=False)
    except Exception as e:
        print(f"Lỗi OCR trang {i}: {e}")
        continue

    # Gom các vùng chữ thành dòng dựa vào tọa độ y
    lines = {}
    for bbox, text, conf in ocr_result:
        y_avg = int(sum([point[1] for point in bbox]) / 4)
        found = False
        for key in lines:
            if abs(key - y_avg) < 15:
                lines[key].append((bbox, text))
                found = True
                break
        if not found:
            lines[y_avg] = [(bbox, text)]

    sorted_lines = [lines[key] for key in sorted(lines.keys())]
    for line in sorted_lines:
        line.sort(key=lambda x: min([point[0] for point in x[0]]))
        results.append(" ".join([text for bbox, text in line]))

    print(f"\n--- Nội dung OCR trang {i} ---")
    for line in sorted_lines:
        print(" ".join([text for bbox, text in line]))

# Xử lý bảng từ OCR
data = []
collecting = False
for line in results:
    if 'không kỳ hạn' in line.lower():
        collecting = True
    if collecting:
        row = re.split(r"\s{2,}", line)
        if len(row) > 1:
            data.append(row)
    if '60 tháng' in line.lower() and collecting:
        break

if data:
    # Nếu đoán được số cột, có thể đặt tên cột ở đây
    df = pd.DataFrame(data)
    print(df.head(10))
else:
    print("Không tìm thấy dữ liệu bảng phù hợp.")