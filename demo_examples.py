#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ví dụ sử dụng Vietnamese PDF Processor
Example usage of Vietnamese PDF Processor
"""

import os
import sys
from vietnamese_pdf_processor import VietnamesePDFProcessor


def demo_basic_usage():
    """Demo cơ bản sử dụng processor"""
    print("=== DEMO CƠ BẢN ===")
    
    # Khởi tạo processor
    processor = VietnamesePDFProcessor(gpu=False, verbose=True)
    
    # Tìm file PDF để demo
    sample_files = ['vpbank_interest_rates.pdf', 'a.pdf', 'sample.pdf']
    
    for pdf_file in sample_files:
        if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
            print(f"\nXử lý file: {pdf_file}")
            try:
                results = processor.process_pdf(pdf_file, output_format='csv')
                
                print(f"\n✅ Kết quả xử lý:")
                print(f"   📄 Tổng số trang: {results['total_pages']}")
                print(f"   ✅ Trang đã xử lý: {results['processed_pages']}")
                print(f"   📊 Số bảng tìm thấy: {len(results['tables'])}")
                
                if results['tables']:
                    print(f"\n📋 Chi tiết bảng:")
                    for table_info in results['tables']:
                        df = table_info['data']
                        print(f"   - Trang {table_info['page']}: {df.shape[0]} hàng × {df.shape[1]} cột")
                        
                        # Hiển thị preview
                        if not df.empty:
                            print(f"   Preview bảng trang {table_info['page']}:")
                            print(df.head(3).to_string(index=False))
                            print()
                
                return True
                
            except Exception as e:
                print(f"❌ Lỗi khi xử lý {pdf_file}: {e}")
                continue
    
    print("❌ Không tìm thấy file PDF hợp lệ để demo")
    return False


def demo_download_from_url():
    """Demo tải và xử lý PDF từ URL"""
    print("\n=== DEMO TẢI PDF TỪ URL ===")
    
    # URL mẫu (thay thế bằng URL thực tế)
    sample_urls = [
        "https://www.vpbank.com.vn/-/media/vpbank-latest/tai-lieu-bieu-mau/lai-suat-huy-dong/khcn/2025/20250708-Bieu-lai-suat-Niem-yet.pdf",
        # Thêm URL khác nếu cần
    ]
    
    processor = VietnamesePDFProcessor(verbose=True)
    
    for url in sample_urls:
        print(f"\nThử tải PDF từ: {url}")
        
        local_file = "downloaded_sample.pdf"
        if processor.download_pdf(url, local_file):
            print(f"✅ Tải thành công, bắt đầu xử lý...")
            
            try:
                results = processor.process_pdf(local_file, output_format='excel')
                print(f"✅ Đã xử lý thành công!")
                
                # Cleanup
                if os.path.exists(local_file):
                    os.remove(local_file)
                    
                return True
                
            except Exception as e:
                print(f"❌ Lỗi khi xử lý: {e}")
        else:
            print("❌ Không thể tải PDF từ URL (có thể do mạng bị chặn)")
    
    return False


def demo_custom_processing():
    """Demo xử lý tùy chỉnh"""
    print("\n=== DEMO XỬ LÝ TÙY CHỈNH ===")
    
    class CustomVietnamesePDFProcessor(VietnamesePDFProcessor):
        """Processor tùy chỉnh với các cải tiến đặc biệt"""
        
        def clean_vietnamese_text(self, text):
            """Tùy chỉnh làm sạch văn bản"""
            # Gọi phương thức gốc
            text = super().clean_vietnamese_text(text)
            
            # Thêm các tùy chỉnh riêng
            replacements = {
                'NGÂN HANG': 'NGÂN HÀNG',
                'LAI SUAT': 'LÃI SUẤT',
                'Tien gui': 'Tiền gửi',
                'KH CN': 'KHCN',
                'VPBank': 'VP Bank'
            }
            
            for old, new in replacements.items():
                text = text.replace(old, new)
            
            return text
    
    # Sử dụng processor tùy chỉnh
    processor = CustomVietnamesePDFProcessor(verbose=True)
    
    # Demo với file mẫu
    sample_files = ['vpbank_interest_rates.pdf', 'a.pdf']
    
    for pdf_file in sample_files:
        if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
            print(f"\nXử lý tùy chỉnh file: {pdf_file}")
            try:
                results = processor.process_pdf(pdf_file, output_format='json')
                print(f"✅ Xử lý tùy chỉnh thành công!")
                return True
            except Exception as e:
                print(f"❌ Lỗi: {e}")
    
    print("❌ Không có file mẫu để demo xử lý tùy chỉnh")
    return False


def create_sample_text_data():
    """Tạo dữ liệu văn bản mẫu để demo"""
    print("\n=== TẠO DỮ LIỆU MẪU ===")
    
    # Tạo file văn bản mẫu mô phỏng kết quả OCR
    sample_text = """
NGÂN HÀNG THƯƠNG MẠI CỔ PHẦN VIỆT NAM THỊNH VƯỢNG
BIỂU LÃI SUẤT NIÊM YẾT

Loại tiền gửi                    Kỳ hạn          Lãi suất (%/năm)
Tiền gửi không kỳ hạn           Không kỳ hạn    0.50
Tiền gửi có kỳ hạn              1 tháng         4.20
                                3 tháng         4.80
                                6 tháng         5.20
                                12 tháng        6.50
                                24 tháng        7.00

Ghi chú:
- Lãi suất áp dụng từ ngày 08/07/2025
- Áp dụng cho khách hàng cá nhân
- Có thể thay đổi mà không báo trước
"""
    
    with open('sample_vietnamese_text.txt', 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    print("✅ Đã tạo file sample_vietnamese_text.txt")
    
    # Tạo CSV mẫu
    import pandas as pd
    
    sample_data = {
        'Loại tiền gửi': [
            'Tiền gửi không kỳ hạn',
            'Tiền gửi có kỳ hạn',
            'Tiền gửi có kỳ hạn', 
            'Tiền gửi có kỳ hạn',
            'Tiền gửi có kỳ hạn',
            'Tiền gửi có kỳ hạn'
        ],
        'Kỳ hạn': [
            'Không kỳ hạn',
            '1 tháng',
            '3 tháng',
            '6 tháng', 
            '12 tháng',
            '24 tháng'
        ],
        'Lãi suất (%/năm)': [0.50, 4.20, 4.80, 5.20, 6.50, 7.00]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('sample_vietnamese_table.csv', index=False, encoding='utf-8-sig')
    
    print("✅ Đã tạo file sample_vietnamese_table.csv")
    print("\nPreview dữ liệu:")
    print(df.to_string(index=False))


def main():
    """Hàm main chạy các demo"""
    print("🇻🇳 VIETNAMESE PDF PROCESSOR - DEMO EXAMPLES 🇻🇳")
    print("=" * 60)
    
    # Tạo dữ liệu mẫu
    create_sample_text_data()
    
    # Chạy các demo
    demos = [
        ("Demo cơ bản", demo_basic_usage),
        ("Demo tải từ URL", demo_download_from_url), 
        ("Demo xử lý tùy chỉnh", demo_custom_processing)
    ]
    
    success_count = 0
    for demo_name, demo_func in demos:
        print(f"\n{'='*20} {demo_name} {'='*20}")
        try:
            if demo_func():
                success_count += 1
                print(f"✅ {demo_name} hoàn thành!")
            else:
                print(f"⚠️ {demo_name} không có dữ liệu để demo")
        except Exception as e:
            print(f"❌ {demo_name} gặp lỗi: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 KẾT QUẢ: {success_count}/{len(demos)} demo chạy thành công")
    
    if success_count == 0:
        print("\n💡 GỢI Ý:")
        print("- Thêm file PDF mẫu vào thư mục để demo")
        print("- Kiểm tra kết nối mạng để tải PDF từ URL")
        print("- Chạy: python vietnamese_pdf_processor.py --help để xem hướng dẫn")


if __name__ == "__main__":
    main()