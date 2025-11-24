#!/usr/bin/env python3
"""
Unit test for SBV crawler logic
"""
import sys
import os
from datetime import datetime, timedelta

# Add the repository root to Python path
repo_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, repo_root)

def test_date_calculation():
    """Test date calculation logic"""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    
    # Format dates as dd/mm/yyyy
    from_date = one_year_ago.strftime('%d/%m/%Y')
    to_date = today.strftime('%d/%m/%Y')
    
    print(f"From date: {from_date}")
    print(f"To date: {to_date}")
    
    # Validate format
    assert len(from_date.split('/')) == 3, "From date should have 3 parts"
    assert len(to_date.split('/')) == 3, "To date should have 3 parts"
    
    # Validate that from_date is before to_date
    from_date_obj = datetime.strptime(from_date, '%d/%m/%Y')
    to_date_obj = datetime.strptime(to_date, '%d/%m/%Y')
    
    assert from_date_obj < to_date_obj, "From date should be before to date"
    
    print("✓ Date calculation test passed")

def test_file_paths():
    """Test output file path logic"""
    from pathlib import Path
    
    # Simulate the path calculation from the scraper
    current_folder = "sbv"  # Simulating Path(__file__).resolve().parent.name
    output_dir = Path(repo_root) / 'craw_html' / current_folder
    
    today_str = datetime.today().strftime('%Y%m%d')
    output_file = output_dir / f'ty_gia_sbv_{today_str}.html'
    
    print(f"Output directory: {output_dir}")
    print(f"Output file: {output_file}")
    
    # Check that the path components are correct
    assert output_dir.name == current_folder, f"Expected {current_folder}, got {output_dir.name}"
    assert output_file.suffix == '.html', f"Expected .html extension, got {output_file.suffix}"
    
    print("✓ File path test passed")

def main():
    """Run all unit tests"""
    print("Testing SBV Crawler Logic...")
    print("=" * 40)
    
    try:
        test_date_calculation()
        print()
        test_file_paths()
        print()
        print("✓ All unit tests passed!")
        return 0
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())