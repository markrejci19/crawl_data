# Hướng dẫn chi tiết xử lý PDF tiếng Việt / Detailed Vietnamese PDF Processing Guide

## Tổng quan / Overview

Dự án này cung cấp giải pháp hoàn chỉnh để xử lý file PDF tiếng Việt dạng ảnh, trích xuất văn bản và bảng biểu mà không cần sử dụng API trả phí.

This project provides a comprehensive solution for processing Vietnamese image-based PDF files, extracting text and tables without requiring paid APIs.

## Cấu trúc dự án / Project Structure

```
crawl_data/
├── vietnamese_pdf_processor.py    # Module chính / Main processor
├── demo_examples.py              # Ví dụ sử dụng / Usage examples  
├── batch_processor.py           # Xử lý batch / Batch processing
├── system_checker.py           # Kiểm tra hệ thống / System checker
├── test_basic.py               # Tests cơ bản / Basic tests
├── config.py                   # Cấu hình / Configuration
├── requirements.txt            # Dependencies
├── README.md                   # Documentation
├── sample_vietnamese_text.txt   # Dữ liệu mẫu / Sample data
└── sample_vietnamese_table.csv  # Bảng mẫu / Sample table
```

## Cài đặt nhanh / Quick Installation

```bash
# 1. Clone repository
git clone https://github.com/markrejci19/crawl_data.git
cd crawl_data

# 2. Cài đặt dependencies
pip install -r requirements.txt

# 3. Cài đặt poppler (để chuyển PDF sang ảnh)
# Ubuntu/Debian:
sudo apt-get install poppler-utils

# MacOS:
brew install poppler

# Windows: Download from https://poppler.freedesktop.org/

# 4. Kiểm tra cài đặt
python test_basic.py
```

## Sử dụng cơ bản / Basic Usage

### 1. Xử lý một file PDF

```python
from vietnamese_pdf_processor import VietnamesePDFProcessor

# Khởi tạo processor
processor = VietnamesePDFProcessor(gpu=False, verbose=True)

# Xử lý PDF
results = processor.process_pdf('document.pdf', output_format='csv')

# Kết quả
print(f"Trang đã xử lý: {results['processed_pages']}")
print(f"Bảng tìm thấy: {len(results['tables'])}")
```

### 2. Xử lý từ command line

```bash
# Xử lý file PDF cục bộ
python vietnamese_pdf_processor.py document.pdf

# Xử lý PDF từ URL
python vietnamese_pdf_processor.py https://example.com/file.pdf --format excel

# Sử dụng GPU (nếu có)
python vietnamese_pdf_processor.py document.pdf --gpu
```

### 3. Xử lý batch nhiều file

```bash
# Xử lý tất cả PDF trong thư mục
python batch_processor.py ./pdf_folder/ --format csv --workers 4

# Với pattern cụ thể
python batch_processor.py ./docs/ --pattern "**/*.pdf" --format excel
```

## Các tính năng nâng cao / Advanced Features

### 1. Tùy chỉnh preprocessing

```python
from PIL import ImageEnhance, ImageFilter

class CustomProcessor(VietnamesePDFProcessor):
    def preprocess_image(self, image):
        # Tăng độ tương phản
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Làm sắc nét
        image = image.filter(ImageFilter.SHARPEN)
        
        return super().preprocess_image(image)

processor = CustomProcessor()
```

### 2. Tùy chỉnh text cleaning

```python
class BankPDFProcessor(VietnamesePDFProcessor):
    def clean_vietnamese_text(self, text):
        text = super().clean_vietnamese_text(text)
        
        # Sửa lỗi OCR thường gặp trong PDF ngân hàng
        bank_corrections = {
            'LAI SUAT': 'LÃI SUẤT',
            'TIEN GUI': 'TIỀN GỬI',
            'NIEM YET': 'NIÊM YẾT'
        }
        
        for old, new in bank_corrections.items():
            text = text.replace(old, new)
            
        return text
```

### 3. Xử lý URL với authentication

```python
processor = VietnamesePDFProcessor()

# Headers tùy chỉnh
headers = {
    'User-Agent': 'Mozilla/5.0...',
    'Authorization': 'Bearer token...'
}

# Override download method để thêm headers
def custom_download(url, output_path):
    response = requests.get(url, headers=headers, stream=True)
    # ... xử lý download
    
processor.download_pdf = custom_download
```

## Tối ưu hóa hiệu suất / Performance Optimization

### 1. Kiểm tra hệ thống

```bash
# Chạy system checker để đánh giá hiệu suất
python system_checker.py
```

### 2. Cấu hình tối ưu

```python
import config

# Cho máy RAM thấp
config.DPI = 200  # Thay vì 300
config.MAX_WORKERS = 1

# Cho máy mạnh
config.DPI = 400
config.MAX_WORKERS = 8
config.USE_GPU = True
```

### 3. Xử lý file lớn

```python
# Chia nhỏ PDF trước khi xử lý
from pdf2image import convert_from_path

def process_large_pdf(pdf_path, batch_size=5):
    pages = convert_from_path(pdf_path, dpi=200)
    
    for i in range(0, len(pages), batch_size):
        batch = pages[i:i+batch_size]
        # Xử lý batch
        # ... 
```

## Xử lý các trường hợp đặc biệt / Special Cases

### 1. PDF có watermark

```python
def remove_watermark(image):
    # Chuyển sang grayscale
    gray = image.convert('L')
    
    # Threshold để loại bỏ watermark nhạt
    threshold = 200
    gray = gray.point(lambda x: 255 if x > threshold else x)
    
    return gray

processor.preprocess_image = remove_watermark
```

### 2. PDF bị nghiêng

```python
import cv2

def auto_rotate(image):
    img_array = np.array(image)
    
    # Detect và sửa góc nghiêng
    edges = cv2.Canny(img_array, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
    
    if lines is not None:
        # Tính góc nghiêng và xoay
        # ... logic xoay ảnh
        pass
    
    return Image.fromarray(img_array)
```

### 3. Bảng phức tạp với merged cells

```python
def detect_complex_table(text_boxes):
    # Phát hiện cell được merge
    # Sử dụng khoảng cách và kích thước để đoán structure
    
    merged_cells = []
    for box in text_boxes:
        if box['width'] > average_width * 1.5:
            # Có thể là merged cell
            merged_cells.append(box)
    
    return merged_cells
```

## Debugging / Gỡ lỗi

### 1. Lưu ảnh trung gian

```python
processor = VietnamesePDFProcessor()
processor.save_intermediate_images = True

# Ảnh sẽ được lưu trong thư mục debug/
```

### 2. Kiểm tra confidence score

```python
results = processor.extract_text_with_positions(image)
low_confidence = [box for box in results if box['confidence'] < 0.7]

print(f"Text boxes với confidence thấp: {len(low_confidence)}")
```

### 3. Log chi tiết

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Trong processor
logger.debug(f"Detected {len(text_boxes)} text boxes")
logger.debug(f"Table structure: {len(rows)} rows")
```

## FAQ / Câu hỏi thường gặp

### Q: Tại sao OCR không chính xác?
A: 
- Kiểm tra chất lượng PDF đầu vào (DPI, độ sắc nét)
- Thử tăng DPI khi convert PDF sang ảnh
- Sử dụng preprocessing để cải thiện ảnh
- Kiểm tra ngôn ngữ OCR (phải có 'vi')

### Q: Làm sao xử lý PDF có mật khẩu?
A:
```python
from PyPDF2 import PdfReader
import pdf2image

def process_protected_pdf(pdf_path, password):
    # Decrypt PDF trước
    reader = PdfReader(pdf_path)
    reader.decrypt(password)
    
    # Sau đó convert sang ảnh
    pages = convert_from_path(pdf_path, dpi=300)
    # ...
```

### Q: Bảng bị detect sai cấu trúc?
A:
- Tăng `TABLE_ROW_THRESHOLD` trong config
- Implement custom table detection logic
- Kiểm tra và điều chỉnh preprocessing

### Q: RAM không đủ khi xử lý file lớn?
A:
- Giảm DPI xuống 200 hoặc 150
- Xử lý từng trang một thay vì toàn bộ
- Sử dụng `MAX_WORKERS = 1`
- Clear cache sau mỗi page

## Roadmap / Kế hoạch phát triển

- [ ] Hỗ trợ table detection bằng computer vision
- [ ] Integration với cloud OCR services
- [ ] GUI application
- [ ] Support cho PDF có text selectable
- [ ] Auto-correction dựa trên dictionary
- [ ] Parallel processing cho large PDFs
- [ ] Export to more formats (Word, PowerPoint)

## Liên hệ / Contact

- GitHub Issues: https://github.com/markrejci19/crawl_data/issues
- Email: support@example.com
- Documentation: https://github.com/markrejci19/crawl_data/wiki