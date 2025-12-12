# Cấu hình xử lý PDF tiếng Việt / Vietnamese PDF Processing Configuration

# OCR Settings
OCR_CONFIDENCE_THRESHOLD = 0.5  # Ngưỡng độ tin cậy OCR (0.0 - 1.0)
OCR_LANGUAGES = ['vi', 'en']     # Ngôn ngữ OCR hỗ trợ
USE_GPU = False                  # Sử dụng GPU cho OCR (cần CUDA)

# Image Processing
DPI = 300                        # Độ phân giải chuyển đổi PDF sang ảnh
IMAGE_ENHANCE_CONTRAST = 1.2     # Hệ số tăng độ tương phản
IMAGE_ENHANCE_BRIGHTNESS = 10    # Tăng độ sáng

# Table Detection
TABLE_ROW_THRESHOLD = 20         # Ngưỡng pixel để phân biệt các hàng
TABLE_MIN_COLS = 2              # Số cột tối thiểu để coi là bảng
TABLE_MIN_ROWS = 2              # Số hàng tối thiểu để coi là bảng

# Text Cleaning
REMOVE_SPECIAL_CHARS = True      # Loại bỏ ký tự đặc biệt
NORMALIZE_NUMBERS = True         # Chuẩn hóa số (1,5 -> 1.5)
CLEAN_WHITESPACE = True         # Chuẩn hóa khoảng trắng

# Output Settings
DEFAULT_OUTPUT_FORMAT = 'csv'    # Định dạng xuất mặc định
INCLUDE_CONFIDENCE = False       # Bao gồm độ tin cậy trong kết quả
SAVE_INTERMEDIATE_IMAGES = False # Lưu ảnh trung gian để debug

# Performance
MAX_WORKERS = 4                  # Số luồng xử lý song song
MEMORY_LIMIT_MB = 1024          # Giới hạn bộ nhớ (MB)
TIMEOUT_SECONDS = 300           # Timeout xử lý (giây)

# Vietnamese Text Corrections
COMMON_OCR_ERRORS = {
    'NGÂN HANG': 'NGÂN HÀNG',
    'LAI SUAT': 'LÃI SUẤT', 
    'TIEN GUI': 'TIỀN GỬI',
    'KH CN': 'KHCN',
    'CHI NHANH': 'CHI NHÁNH',
    'SO DU': 'SỐ DƯ',
    'NIEM YET': 'NIÊM YẾT',
    'THUONG MAI': 'THƯƠNG MẠI',
    'CO PHAN': 'CỔ PHẦN'
}