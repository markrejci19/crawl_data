#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Công cụ xử lý PDF tiếng Việt - Trích xuất văn bản và bảng biểu
Vietnamese PDF Processing Tool - Extract text and tables
"""

from pdf2image import convert_from_path
import easyocr
import pandas as pd
import re
import os
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import requests
from typing import List, Dict, Tuple, Optional
import json
import sys
from datetime import datetime


class VietnamesePDFProcessor:
    """Lớp xử lý PDF tiếng Việt với khả năng trích xuất văn bản và bảng biểu chính xác"""
    
    def __init__(self, gpu: bool = False, verbose: bool = True):
        """
        Khởi tạo processor
        Args:
            gpu (bool): Sử dụng GPU cho OCR (nếu có)
            verbose (bool): In chi tiết quá trình xử lý
        """
        self.reader = easyocr.Reader(['vi', 'en'], gpu=gpu)
        self.verbose = verbose
        self.processed_pages = []
        
    def download_pdf(self, url: str, output_path: str) -> bool:
        """
        Tải xuống PDF từ URL
        Args:
            url (str): URL của file PDF
            output_path (str): Đường dẫn lưu file
        Returns:
            bool: True nếu tải thành công
        """
        try:
            if self.verbose:
                print(f"Đang tải xuống PDF từ: {url}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if self.verbose:
                print(f"Đã tải xuống thành công: {output_path}")
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Lỗi khi tải xuống PDF: {e}")
            return False
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Tiền xử lý ảnh để cải thiện độ chính xác OCR
        Args:
            image (PIL.Image): Ảnh gốc
        Returns:
            PIL.Image: Ảnh đã được xử lý
        """
        # Chuyển sang numpy array
        img_array = np.array(image)
        
        # Chuyển sang grayscale nếu cần
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Khử nhiễu
        img_array = cv2.medianBlur(img_array, 3)
        
        # Cải thiện độ tương phản
        img_array = cv2.convertScaleAbs(img_array, alpha=1.2, beta=10)
        
        # Làm sắc nét
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        img_array = cv2.filter2D(img_array, -1, kernel)
        
        # Chuyển về PIL Image
        return Image.fromarray(img_array)
    
    def extract_text_with_positions(self, image: Image.Image) -> List[Dict]:
        """
        Trích xuất văn bản với thông tin vị trí
        Args:
            image (PIL.Image): Ảnh cần OCR
        Returns:
            List[Dict]: Danh sách các text box với thông tin vị trí
        """
        # Tiền xử lý ảnh
        processed_img = self.preprocess_image(image)
        
        # OCR với thông tin chi tiết
        results = self.reader.readtext(np.array(processed_img), detail=1, paragraph=False)
        
        text_boxes = []
        for (bbox, text, confidence) in results:
            if confidence > 0.5:  # Chỉ lấy text có độ tin cậy cao
                # Tính toán vị trí trung tâm
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                center_x = sum(x_coords) / len(x_coords)
                center_y = sum(y_coords) / len(y_coords)
                
                text_boxes.append({
                    'text': text.strip(),
                    'bbox': bbox,
                    'center_x': center_x,
                    'center_y': center_y,
                    'confidence': confidence,
                    'width': max(x_coords) - min(x_coords),
                    'height': max(y_coords) - min(y_coords)
                })
        
        return text_boxes
    
    def detect_table_structure(self, text_boxes: List[Dict]) -> List[List[Dict]]:
        """
        Phát hiện cấu trúc bảng từ các text box
        Args:
            text_boxes (List[Dict]): Danh sách text boxes
        Returns:
            List[List[Dict]]: Cấu trúc bảng (rows x cols)
        """
        if not text_boxes:
            return []
        
        # Sắp xếp theo vị trí Y (hàng ngang)
        text_boxes_sorted = sorted(text_boxes, key=lambda x: x['center_y'])
        
        # Nhóm các text box thành hàng
        rows = []
        current_row = [text_boxes_sorted[0]]
        current_y = text_boxes_sorted[0]['center_y']
        
        for box in text_boxes_sorted[1:]:
            # Nếu khác biệt Y > 20 pixel, tạo hàng mới
            if abs(box['center_y'] - current_y) > 20:
                # Sắp xếp hàng hiện tại theo X
                current_row.sort(key=lambda x: x['center_x'])
                rows.append(current_row)
                current_row = [box]
                current_y = box['center_y']
            else:
                current_row.append(box)
        
        # Thêm hàng cuối
        if current_row:
            current_row.sort(key=lambda x: x['center_x'])
            rows.append(current_row)
        
        return rows
    
    def clean_vietnamese_text(self, text: str) -> str:
        """
        Làm sạch văn bản tiếng Việt
        Args:
            text (str): Văn bản gốc
        Returns:
            str: Văn bản đã được làm sạch
        """
        if not text:
            return ""
        
        # Loại bỏ ký tự đặc biệt không cần thiết
        text = re.sub(r'[^\w\s\-.,:%/()]', '', text, flags=re.UNICODE)
        
        # Chuẩn hóa khoảng trắng
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Xử lý số và dấu thập phân - chỉ thay thế dấu phẩy giữa các chữ số
        text = re.sub(r'(\d),(\d)', r'\1.\2', text)
        
        return text
    
    def process_pdf(self, pdf_path: str, output_format: str = 'csv') -> Dict:
        """
        Xử lý toàn bộ file PDF
        Args:
            pdf_path (str): Đường dẫn file PDF
            output_format (str): Định dạng xuất ('csv', 'excel', 'json')
        Returns:
            Dict: Kết quả xử lý
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Không tìm thấy file PDF: {pdf_path}")
        
        if self.verbose:
            print(f"Bắt đầu xử lý PDF: {pdf_path}")
        
        try:
            # Chuyển PDF thành ảnh
            pages = convert_from_path(pdf_path, dpi=300)
            if self.verbose:
                print(f"Đã chuyển đổi {len(pages)} trang thành ảnh")
        
        except Exception as e:
            raise Exception(f"Lỗi khi chuyển PDF sang ảnh: {e}")
        
        all_tables = []
        all_text = []
        
        for i, page in enumerate(pages, start=1):
            if self.verbose:
                print(f"\nXử lý trang {i}/{len(pages)}...")
            
            try:
                # Trích xuất text với vị trí
                text_boxes = self.extract_text_with_positions(page)
                
                if self.verbose:
                    print(f"Tìm thấy {len(text_boxes)} text boxes")
                
                # Phát hiện cấu trúc bảng
                table_rows = self.detect_table_structure(text_boxes)
                
                if table_rows:
                    # Chuyển đổi thành DataFrame
                    table_data = []
                    for row in table_rows:
                        row_data = [self.clean_vietnamese_text(box['text']) for box in row]
                        table_data.append(row_data)
                    
                    if table_data:
                        # Chuẩn hóa số cột
                        max_cols = max(len(row) for row in table_data)
                        for row in table_data:
                            while len(row) < max_cols:
                                row.append('')
                        
                        df = pd.DataFrame(table_data)
                        all_tables.append({
                            'page': i,
                            'data': df,
                            'raw_text_boxes': text_boxes
                        })
                
                # Lưu toàn bộ văn bản
                page_text = []
                for box in sorted(text_boxes, key=lambda x: (x['center_y'], x['center_x'])):
                    clean_text = self.clean_vietnamese_text(box['text'])
                    if clean_text:
                        page_text.append(clean_text)
                
                all_text.append({
                    'page': i,
                    'text': '\n'.join(page_text),
                    'text_boxes': text_boxes
                })
                
            except Exception as e:
                if self.verbose:
                    print(f"Lỗi khi xử lý trang {i}: {e}")
                continue
        
        # Tổng hợp kết quả
        result = {
            'success': True,
            'total_pages': len(pages),
            'processed_pages': len(all_text),
            'tables': all_tables,
            'text': all_text,
            'timestamp': datetime.now().isoformat()
        }
        
        # Xuất kết quả
        self._export_results(result, pdf_path, output_format)
        
        return result
    
    def _export_results(self, results: Dict, pdf_path: str, output_format: str):
        """Xuất kết quả ra file"""
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        if output_format.lower() == 'csv':
            # Xuất bảng thành CSV
            for i, table_info in enumerate(results['tables']):
                output_file = f"{base_name}_table_{table_info['page']}.csv"
                table_info['data'].to_csv(output_file, index=False, encoding='utf-8-sig')
                if self.verbose:
                    print(f"Đã xuất bảng trang {table_info['page']}: {output_file}")
            
            # Xuất văn bản
            text_file = f"{base_name}_text.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                for text_info in results['text']:
                    f.write(f"=== TRANG {text_info['page']} ===\n")
                    f.write(text_info['text'])
                    f.write("\n\n")
            
            if self.verbose:
                print(f"Đã xuất văn bản: {text_file}")
        
        elif output_format.lower() == 'excel':
            # Xuất tất cả bảng vào một file Excel
            if results['tables']:
                output_file = f"{base_name}_tables.xlsx"
                with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                    for table_info in results['tables']:
                        sheet_name = f"Trang_{table_info['page']}"
                        table_info['data'].to_excel(writer, sheet_name=sheet_name, index=False)
                
                if self.verbose:
                    print(f"Đã xuất Excel: {output_file}")
        
        elif output_format.lower() == 'json':
            # Xuất JSON (không bao gồm DataFrame)
            json_results = {
                'success': results['success'],
                'total_pages': results['total_pages'],
                'processed_pages': results['processed_pages'],
                'timestamp': results['timestamp'],
                'text': results['text']
            }
            
            output_file = f"{base_name}_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_results, f, ensure_ascii=False, indent=2)
            
            if self.verbose:
                print(f"Đã xuất JSON: {output_file}")


def main():
    """Hàm main để chạy script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Xử lý PDF tiếng Việt - Trích xuất văn bản và bảng biểu')
    parser.add_argument('pdf_path', help='Đường dẫn file PDF hoặc URL')
    parser.add_argument('--format', choices=['csv', 'excel', 'json'], default='csv',
                        help='Định dạng xuất kết quả (mặc định: csv)')
    parser.add_argument('--gpu', action='store_true', help='Sử dụng GPU cho OCR')
    parser.add_argument('--quiet', action='store_true', help='Không in chi tiết quá trình')
    
    args = parser.parse_args()
    
    # Khởi tạo processor
    processor = VietnamesePDFProcessor(gpu=args.gpu, verbose=not args.quiet)
    
    # Xử lý URL hoặc file local
    pdf_path = args.pdf_path
    if pdf_path.startswith(('http://', 'https://')):
        # Tải xuống từ URL
        local_path = 'downloaded_pdf.pdf'
        if not processor.download_pdf(pdf_path, local_path):
            print("Không thể tải xuống PDF từ URL")
            sys.exit(1)
        pdf_path = local_path
    
    try:
        # Xử lý PDF
        results = processor.process_pdf(pdf_path, args.format)
        
        print(f"\n=== KẾT QUẢ XỬ LÝ ===")
        print(f"Tổng số trang: {results['total_pages']}")
        print(f"Trang đã xử lý: {results['processed_pages']}")
        print(f"Số bảng tìm thấy: {len(results['tables'])}")
        
        if results['tables']:
            print("\nChi tiết bảng:")
            for table_info in results['tables']:
                print(f"  - Trang {table_info['page']}: {table_info['data'].shape[0]} hàng, {table_info['data'].shape[1]} cột")
    
    except Exception as e:
        print(f"Lỗi: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Demo với file mẫu
    if len(sys.argv) == 1:
        print("=== DEMO XỬ LÝ PDF TIẾNG VIỆT ===")
        print("Sử dụng: python vietnamese_pdf_processor.py <đường_dẫn_pdf> [--format csv|excel|json] [--gpu] [--quiet]")
        print("\nVí dụ:")
        print("  python vietnamese_pdf_processor.py document.pdf")
        print("  python vietnamese_pdf_processor.py https://example.com/document.pdf --format excel")
        print("  python vietnamese_pdf_processor.py document.pdf --gpu --format json")
        
        # Nếu có file PDF mẫu, xử lý nó
        sample_files = ['a.pdf', 'vpbank_interest_rates.pdf']
        for sample_file in sample_files:
            if os.path.exists(sample_file) and os.path.getsize(sample_file) > 0:
                print(f"\nTìm thấy file mẫu: {sample_file}")
                print("Đang xử lý...")
                
                processor = VietnamesePDFProcessor(verbose=True)
                try:
                    results = processor.process_pdf(sample_file)
                    print(f"Hoàn thành! Tìm thấy {len(results['tables'])} bảng")
                except Exception as e:
                    print(f"Lỗi khi xử lý file mẫu: {e}")
                break
        else:
            print("\nKhông tìm thấy file PDF mẫu để demo.")
    else:
        main()