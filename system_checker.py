#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Công cụ kiểm tra và tối ưu hóa hiệu suất
Performance checker and optimizer for Vietnamese PDF Processing
"""

import time
import psutil
import os
import sys
from vietnamese_pdf_processor import VietnamesePDFProcessor
import config


def check_system_requirements():
    """Kiểm tra yêu cầu hệ thống"""
    print("=== KIỂM TRA HỆ THỐNG ===")
    
    # Kiểm tra Python version
    python_version = sys.version_info
    print(f"🐍 Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("⚠️ Cảnh báo: Nên sử dụng Python 3.7 trở lên")
    else:
        print("✅ Phiên bản Python phù hợp")
    
    # Kiểm tra RAM
    memory = psutil.virtual_memory()
    total_gb = memory.total / (1024**3)
    available_gb = memory.available / (1024**3)
    
    print(f"💾 RAM: {total_gb:.1f}GB tổng / {available_gb:.1f}GB khả dụng")
    
    if available_gb < 2:
        print("⚠️ Cảnh báo: RAM thấp, có thể xử lý chậm")
    else:
        print("✅ RAM đủ để xử lý")
    
    # Kiểm tra CPU
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    print(f"🖥️ CPU: {cpu_count} cores, {cpu_percent}% sử dụng")
    
    # Kiểm tra disk space
    disk = psutil.disk_usage('.')
    free_gb = disk.free / (1024**3)
    
    print(f"💿 Disk: {free_gb:.1f}GB trống")
    
    if free_gb < 1:
        print("⚠️ Cảnh báo: Dung lượng disk thấp")
    else:
        print("✅ Dung lượng disk đủ")


def check_dependencies():
    """Kiểm tra các thư viện cần thiết"""
    print("\n=== KIỂM TRA THƯ VIỆN ===")
    
    required_packages = [
        'pdf2image',
        'easyocr', 
        'pandas',
        'opencv-python',
        'numpy',
        'pillow',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Chưa cài đặt")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Cần cài đặt: pip install {' '.join(missing_packages)}")
        return False
    else:
        print("\n✅ Tất cả thư viện đã được cài đặt")
        return True


def benchmark_ocr_performance():
    """Đo hiệu suất OCR"""
    print("\n=== ĐO HIỆU SUẤT OCR ===")
    
    try:
        # Tạo processor
        start_time = time.time()
        processor = VietnamesePDFProcessor(verbose=False)
        init_time = time.time() - start_time
        
        print(f"⏱️ Thời gian khởi tạo EasyOCR: {init_time:.2f}s")
        
        if init_time > 30:
            print("⚠️ Khởi tạo chậm, có thể do tải model lần đầu")
        else:
            print("✅ Khởi tạo nhanh")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khởi tạo OCR: {e}")
        return False


def optimize_settings():
    """Gợi ý tối ưu hóa cài đặt"""
    print("\n=== GỢI Ý TỐI ƯU HÓA ===")
    
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024**3)
    cpu_count = psutil.cpu_count()
    
    # Gợi ý DPI
    if available_gb < 4:
        recommended_dpi = 200
        print(f"💡 RAM thấp - Gợi ý DPI: {recommended_dpi} (thay vì {config.DPI})")
    else:
        recommended_dpi = 300
        print(f"✅ DPI khuyến nghị: {recommended_dpi}")
    
    # Gợi ý số workers
    if cpu_count >= 4:
        recommended_workers = min(4, cpu_count // 2)
    else:
        recommended_workers = 1
    
    print(f"💡 Số workers khuyến nghị: {recommended_workers}")
    
    # Gợi ý GPU
    try:
        import torch
        if torch.cuda.is_available():
            print("🚀 CUDA khả dụng - Có thể sử dụng --gpu để tăng tốc")
        else:
            print("💻 Chỉ có CPU - Sử dụng chế độ CPU")
    except ImportError:
        print("💻 PyTorch chưa cài đặt - Sử dụng chế độ CPU")
    
    return {
        'dpi': recommended_dpi,
        'workers': recommended_workers,
        'gpu': False
    }


def create_optimized_config(optimizations):
    """Tạo file config tối ưu"""
    print("\n=== TẠO CONFIG TỐI ƯU ===")
    
    config_content = f"""# Cấu hình tối ưu được tạo tự động
# Auto-generated optimized configuration

# OCR Settings
OCR_CONFIDENCE_THRESHOLD = 0.5
OCR_LANGUAGES = ['vi', 'en']
USE_GPU = {optimizations['gpu']}

# Image Processing  
DPI = {optimizations['dpi']}
IMAGE_ENHANCE_CONTRAST = 1.2
IMAGE_ENHANCE_BRIGHTNESS = 10

# Performance
MAX_WORKERS = {optimizations['workers']}
MEMORY_LIMIT_MB = 1024
TIMEOUT_SECONDS = 300

# Table Detection
TABLE_ROW_THRESHOLD = 20
TABLE_MIN_COLS = 2
TABLE_MIN_ROWS = 2

# Output Settings
DEFAULT_OUTPUT_FORMAT = 'csv'
INCLUDE_CONFIDENCE = False
SAVE_INTERMEDIATE_IMAGES = False
"""
    
    with open('config_optimized.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Đã tạo config_optimized.py")


def main():
    """Hàm main"""
    print("🇻🇳 VIETNAMESE PDF PROCESSOR - SYSTEM CHECKER 🇻🇳")
    print("=" * 60)
    
    # Kiểm tra hệ thống
    check_system_requirements()
    
    # Kiểm tra dependencies
    if not check_dependencies():
        print("\n❌ Vui lòng cài đặt các thư viện thiếu trước khi tiếp tục")
        return
    
    # Đo hiệu suất OCR
    if not benchmark_ocr_performance():
        print("\n❌ Có vấn đề với OCR engine")
        return
    
    # Tối ưu hóa
    optimizations = optimize_settings()
    create_optimized_config(optimizations)
    
    print("\n" + "=" * 60)
    print("✅ Kiểm tra hoàn thành!")
    print("\n💡 KHUYẾN NGHỊ:")
    print("1. Sử dụng file config_optimized.py cho hiệu suất tốt nhất")
    print("2. Xử lý file PDF nhỏ trước để test")
    print("3. Giám sát việc sử dụng RAM khi xử lý file lớn")
    print("4. Chạy: python vietnamese_pdf_processor.py --help để xem hướng dẫn")


if __name__ == "__main__":
    main()