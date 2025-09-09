#!/usr/bin/env python3
"""
Demo script to showcase MOF Data Extractor functionality

This script demonstrates the extractor's capabilities using mock data
without requiring internet access.
"""

import pandas as pd
import numpy as np
from mof_extractor import MOFDataExtractor

def create_demo_data():
    """Create sample data that mimics extracted MOF tables"""
    
    # Sample data for Table 4.02
    table_4_02 = pd.DataFrame({
        'Chỉ tiêu': [
            'Nợ công so với tổng sản phẩm quốc dân(GDP) (%)',
            'a. Nợ Chính phủ so với tổng sản phẩm quốc dân (GDP) (%)',
            'b. Nợ Chính phủ bảo lãnh so với tổng sản phẩm quốc dân (GDP) (%)',
            'c. Nợ Chính quyền địa phương so với tổng sản phẩm quốc dân (GDP) (%)'
        ],
        '2019': [55.0, 48.0, 6.7, 0.7],
        '2020': [55.9, 49.9, 5.8, 0.7],
        '2021': [42.7, 38.7, 3.8, 0.6],
        '2022 (P)': [37.4, 34.2, 3.1, 0.6]
    })
    
    # Sample data for Table 4.03
    table_4_03 = pd.DataFrame({
        'Year': ['2020', '2020', '2021', '2021'],
        'Currency': ['USD', 'VND', 'USD', 'VND'],
        'DƯ NỢ': [130118.98, 3016287.89, 139529.60, 3226761.46],
        'Nợ nước ngoài của Chính phủ': [49008.24, 1136059.94, 46552.13, 1076564.56],
        'Nợ nước ngoài của doanh nghiệp': [81110.74, 1880227.95, 92977.47, 2150196.90]
    })
    
    return {
        'Mẫu biểu công bố thông tin số 4.02': table_4_02,
        'Mẫu biểu công khai thông tin số 4.03': table_4_03
    }

def demo_processing_methods():
    """Demonstrate the coordinate processing methods"""
    print("=" * 60)
    print("DEMO: Coordinate Processing Methods")
    print("=" * 60)
    
    extractor = MOFDataExtractor()
    
    # Sample coordinate data (top, left, text)
    sample_coords = [
        (100, 50, "Chỉ tiêu"),
        (100, 150, "2019"),
        (100, 200, "2020"),
        (120, 50, "Nợ công"),
        (120, 150, "55,0"),
        (120, 200, "55,9"),
        (140, 50, "Nợ Chính phủ"),
        (140, 150, "48,0"),
        (140, 200, "49,9")
    ]
    
    print("Original coordinates:")
    for coord in sample_coords:
        print(f"  {coord}")
    
    print("\nAfter process_adjacent_coordinates2:")
    processed = extractor.process_adjacent_coordinates2(sample_coords)
    for coord in processed:
        print(f"  {coord}")
    
    print("\nAfter grouping by top coordinate:")
    lines = {}
    for top, left, txt in processed:
        key = round(top, 0)
        lines.setdefault(key, []).append(txt)
    
    for key in sorted(lines.keys()):
        print(f"  Line {key}: {lines[key]}")

def demo_extraction_simulation():
    """Simulate the extraction process with mock data"""
    print("\n" + "=" * 60)
    print("DEMO: Simulated Data Extraction")
    print("=" * 60)
    
    # Create demo data
    demo_data = create_demo_data()
    
    print("Simulated extraction from MOF website:")
    print(f"URL: https://mof.gov.vn/bo-tai-chinh/ban-tin-no-cong/mofucm304557")
    print()
    
    for table_name, df in demo_data.items():
        print(f"Table: {table_name}")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print("  Sample data:")
        print(df.head(3).to_string(index=False, max_cols=6))
        print()
    
    # Demonstrate saving functionality
    extractor = MOFDataExtractor()
    print("Saving demo data...")
    
    # Save as Excel (simulated)
    print("  ✓ Would save to Excel file: mof_extracted_data_[timestamp].xlsx")
    
    # Show what the save method would do
    print("\nExcel sheets that would be created:")
    for table_name in demo_data.keys():
        sheet_name = table_name.replace('Mẫu biểu công bố thông tin số ', 'Table_')
        sheet_name = sheet_name.replace('Mẫu biểu công khai thông tin số ', 'Public_Table_')
        sheet_name = sheet_name[:31]
        print(f"  - {sheet_name}")

def demo_error_handling():
    """Demonstrate error handling capabilities"""
    print("\n" + "=" * 60)
    print("DEMO: Error Handling")
    print("=" * 60)
    
    extractor = MOFDataExtractor()
    
    # Test with empty data
    print("Testing with empty data:")
    result = extractor.clean_lists([])
    print(f"  Empty list result: {result}")
    
    # Test with malformed data  
    print("\nTesting with data containing patterns to remove:")
    test_data = [["col1", "col2", "(1)", "col3", "(2)", "col4", "col5"]]
    cleaned = extractor.clean_lists(test_data)
    print(f"  Original: {test_data[0]}")
    print(f"  Cleaned:  {cleaned[0] if cleaned else 'No data'}")
    
    # Test save with no data
    print("\nTesting save with no data:")
    extractor.save_results({})

def main():
    """Run the demo"""
    print("MOF Data Extractor - Functionality Demo")
    print("This demo shows the extractor's capabilities without web access")
    
    # Demo coordinate processing
    demo_processing_methods()
    
    # Demo extraction simulation
    demo_extraction_simulation()
    
    # Demo error handling
    demo_error_handling()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("To extract real data, run: python mof_extractor.py")
    print("To see usage examples, run: python example_usage.py")
    print("To run tests, run: python test_extractor.py")

if __name__ == "__main__":
    main()