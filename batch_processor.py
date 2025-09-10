#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Công cụ xử lý batch nhiều file PDF
Batch processing tool for multiple PDF files
"""

import os
import sys
import glob
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from vietnamese_pdf_processor import VietnamesePDFProcessor


class BatchPDFProcessor:
    """Lớp xử lý batch nhiều PDF"""
    
    def __init__(self, max_workers=2, gpu=False, verbose=True):
        """
        Khởi tạo batch processor
        Args:
            max_workers (int): Số luồng xử lý song song
            gpu (bool): Sử dụng GPU
            verbose (bool): In chi tiết
        """
        self.max_workers = max_workers
        self.gpu = gpu
        self.verbose = verbose
        self.results = []
        
    def find_pdf_files(self, directory, pattern="*.pdf"):
        """
        Tìm tất cả file PDF trong thư mục
        Args:
            directory (str): Thư mục tìm kiếm
            pattern (str): Pattern file (mặc định: *.pdf)
        Returns:
            list: Danh sách đường dẫn PDF
        """
        if not os.path.isdir(directory):
            raise ValueError(f"Thư mục không tồn tại: {directory}")
        
        search_pattern = os.path.join(directory, pattern)
        pdf_files = glob.glob(search_pattern, recursive=True)
        
        # Lọc file có kích thước > 0
        valid_files = []
        for pdf_file in pdf_files:
            if os.path.getsize(pdf_file) > 0:
                valid_files.append(pdf_file)
            elif self.verbose:
                print(f"⚠️ Bỏ qua file rỗng: {pdf_file}")
        
        return valid_files
    
    def process_single_pdf(self, pdf_path, output_format='csv'):
        """
        Xử lý một file PDF
        Args:
            pdf_path (str): Đường dẫn PDF
            output_format (str): Định dạng xuất
        Returns:
            dict: Kết quả xử lý
        """
        start_time = datetime.now()
        
        try:
            if self.verbose:
                print(f"🔄 Bắt đầu xử lý: {os.path.basename(pdf_path)}")
            
            processor = VietnamesePDFProcessor(gpu=self.gpu, verbose=False)
            results = processor.process_pdf(pdf_path, output_format)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            result = {
                'file': pdf_path,
                'status': 'success',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(), 
                'processing_time': processing_time,
                'total_pages': results['total_pages'],
                'processed_pages': results['processed_pages'],
                'tables_found': len(results['tables']),
                'error': None
            }
            
            if self.verbose:
                print(f"✅ Hoàn thành: {os.path.basename(pdf_path)} "
                      f"({processing_time:.1f}s, {len(results['tables'])} bảng)")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            result = {
                'file': pdf_path,
                'status': 'error',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'processing_time': processing_time,
                'total_pages': 0,
                'processed_pages': 0,
                'tables_found': 0,
                'error': str(e)
            }
            
            if self.verbose:
                print(f"❌ Lỗi: {os.path.basename(pdf_path)} - {e}")
            
            return result
    
    def process_batch(self, pdf_files, output_format='csv'):
        """
        Xử lý batch nhiều PDF
        Args:
            pdf_files (list): Danh sách đường dẫn PDF
            output_format (str): Định dạng xuất
        Returns:
            dict: Tổng kết kết quả
        """
        if not pdf_files:
            raise ValueError("Không có file PDF nào để xử lý")
        
        batch_start = datetime.now()
        
        if self.verbose:
            print(f"🚀 Bắt đầu xử lý batch {len(pdf_files)} file PDF")
            print(f"⚙️ Cấu hình: {self.max_workers} workers, GPU: {self.gpu}")
        
        results = []
        
        # Xử lý song song
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tất cả jobs
            future_to_file = {
                executor.submit(self.process_single_pdf, pdf_file, output_format): pdf_file 
                for pdf_file in pdf_files
            }
            
            # Collect kết quả
            for future in as_completed(future_to_file):
                result = future.result()
                results.append(result)
        
        batch_end = datetime.now()
        total_time = (batch_end - batch_start).total_seconds()
        
        # Tổng kết
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']
        
        total_pages = sum(r['total_pages'] for r in successful)
        total_tables = sum(r['tables_found'] for r in successful)
        
        summary = {
            'batch_start': batch_start.isoformat(),
            'batch_end': batch_end.isoformat(),
            'total_time': total_time,
            'total_files': len(pdf_files),
            'successful_files': len(successful),
            'failed_files': len(failed),
            'total_pages': total_pages,
            'total_tables': total_tables,
            'average_time_per_file': total_time / len(pdf_files) if pdf_files else 0,
            'results': results
        }
        
        if self.verbose:
            print(f"\n📊 KẾT QUẢ BATCH:")
            print(f"   ✅ Thành công: {len(successful)}/{len(pdf_files)} file")
            print(f"   ❌ Thất bại: {len(failed)} file")
            print(f"   📄 Tổng trang: {total_pages}")
            print(f"   📊 Tổng bảng: {total_tables}")
            print(f"   ⏱️ Thời gian: {total_time:.1f}s")
            
            if failed:
                print(f"\n❌ File lỗi:")
                for result in failed:
                    print(f"   - {os.path.basename(result['file'])}: {result['error']}")
        
        return summary
    
    def save_batch_report(self, summary, output_file='batch_report.json'):
        """
        Lưu báo cáo batch
        Args:
            summary (dict): Tổng kết kết quả
            output_file (str): File báo cáo
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        if self.verbose:
            print(f"📄 Đã lưu báo cáo: {output_file}")


def main():
    """Hàm main"""
    parser = argparse.ArgumentParser(description='Xử lý batch nhiều file PDF tiếng Việt')
    parser.add_argument('directory', help='Thư mục chứa file PDF')
    parser.add_argument('--pattern', default='*.pdf', help='Pattern tìm file (mặc định: *.pdf)')
    parser.add_argument('--format', choices=['csv', 'excel', 'json'], default='csv',
                        help='Định dạng xuất (mặc định: csv)')
    parser.add_argument('--workers', type=int, default=2, help='Số luồng xử lý (mặc định: 2)')
    parser.add_argument('--gpu', action='store_true', help='Sử dụng GPU')
    parser.add_argument('--quiet', action='store_true', help='Không in chi tiết')
    parser.add_argument('--report', default='batch_report.json', help='File báo cáo')
    
    args = parser.parse_args()
    
    try:
        # Khởi tạo batch processor
        processor = BatchPDFProcessor(
            max_workers=args.workers,
            gpu=args.gpu,
            verbose=not args.quiet
        )
        
        # Tìm file PDF
        pdf_files = processor.find_pdf_files(args.directory, args.pattern)
        
        if not pdf_files:
            print(f"❌ Không tìm thấy file PDF nào trong: {args.directory}")
            sys.exit(1)
        
        # Xử lý batch
        summary = processor.process_batch(pdf_files, args.format)
        
        # Lưu báo cáo
        processor.save_batch_report(summary, args.report)
        
        # Exit code
        if summary['failed_files'] > 0:
            sys.exit(1)  # Có lỗi
        else:
            sys.exit(0)  # Thành công
            
    except Exception as e:
        print(f"❌ Lỗi batch processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Demo nếu không có arguments
    if len(sys.argv) == 1:
        print("=== BATCH PDF PROCESSOR DEMO ===")
        print("Sử dụng: python batch_processor.py <thư_mục> [options]")
        print("\nVí dụ:")
        print("  python batch_processor.py ./pdfs/")
        print("  python batch_processor.py ./docs/ --format excel --workers 4")
        print("  python batch_processor.py ./files/ --pattern '**/*.pdf' --gpu")
        
        # Demo với thư mục hiện tại
        current_dir = "."
        batch_processor = BatchPDFProcessor(max_workers=1, verbose=True)
        
        try:
            pdf_files = batch_processor.find_pdf_files(current_dir)
            if pdf_files:
                print(f"\nTìm thấy {len(pdf_files)} file PDF trong thư mục hiện tại:")
                for pdf_file in pdf_files:
                    size_mb = os.path.getsize(pdf_file) / (1024*1024)
                    print(f"  - {pdf_file} ({size_mb:.1f}MB)")
                
                print(f"\nChạy demo với file đầu tiên...")
                demo_summary = batch_processor.process_batch([pdf_files[0]], 'csv')
                batch_processor.save_batch_report(demo_summary, 'demo_batch_report.json')
            else:
                print(f"\nKhông tìm thấy file PDF nào trong thư mục hiện tại")
                
        except Exception as e:
            print(f"Demo lỗi: {e}")
    else:
        main()