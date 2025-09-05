#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to validate UTF-8 encoding in the CSV output files
"""

import pandas as pd
import os

def test_utf8_encoding():
    """Test that all output CSV files are properly UTF-8 encoded"""
    
    print("Testing UTF-8 encoding of output files...")
    
    # Test files that should be UTF-8
    utf8_files = [
        "sbv_data_IV_2024_v1_20250904.csv",
        "result_new.csv"
    ]
    
    for filename in utf8_files:
        if os.path.exists(filename):
            try:
                # Try to read the file with UTF-8 encoding
                df = pd.read_csv(filename, encoding='utf-8')
                print(f"✓ {filename}: Successfully read with UTF-8 encoding")
                
                # Check that Vietnamese characters are properly displayed
                vietnamese_chars_found = False
                for col in df.columns:
                    if df[col].dtype == 'object':  # String columns
                        for value in df[col].dropna():
                            if any(char in str(value) for char in 'áàảãạâấầẩẫậăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ'):
                                vietnamese_chars_found = True
                                print(f"  ✓ Vietnamese characters properly encoded: {value[:50]}...")
                                break
                        if vietnamese_chars_found:
                            break
                
                if not vietnamese_chars_found:
                    print(f"  ! No Vietnamese characters found in {filename}")
                    
            except UnicodeDecodeError as e:
                print(f"✗ {filename}: Failed to read with UTF-8 encoding - {e}")
                return False
            except Exception as e:
                print(f"✗ {filename}: Error reading file - {e}")
                return False
        else:
            print(f"! {filename}: File not found")
    
    print("\nUTF-8 encoding test completed successfully!")
    return True

if __name__ == "__main__":
    test_utf8_encoding()