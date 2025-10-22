#!/usr/bin/env python3
"""
Example usage of MOF Data Extractor

This script demonstrates how to use the MOF Data Extractor
to extract tables from the Vietnamese Ministry of Finance website.
"""

from mof_extractor import MOFDataExtractor

def main():
    """Example of using the MOF Data Extractor"""
    
    # URL to extract data from
    url = "https://mof.gov.vn/bo-tai-chinh/ban-tin-no-cong/mofucm304557"
    
    print("MOF Data Extraction Example")
    print("=" * 40)
    print(f"Extracting data from: {url}")
    print()
    
    # Option 1: Using context manager (recommended)
    print("Using context manager approach:")
    try:
        with MOFDataExtractor(headless=True) as extractor:
            data = extractor.extract_all_tables(url)
            
            if data:
                print(f"Successfully extracted {len(data)} tables:")
                for table_name in data.keys():
                    print(f"  - {table_name}")
                
                # Save to Excel file
                extractor.save_results(data, 'excel')
                
            else:
                print("No data was extracted")
                
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 40)
    
    # Option 2: Manual setup and cleanup
    print("Manual setup approach:")
    extractor = None
    try:
        extractor = MOFDataExtractor(headless=True)
        extractor.setup_driver()
        
        # Extract specific table
        table_name = 'Mẫu biểu công bố thông tin số 4.02'
        df = extractor.extract_table_from_page(table_name)
        
        if df is not None:
            print(f"Extracted table '{table_name}' with {len(df)} rows")
            print("Sample data:")
            print(df.head())
        else:
            print(f"Failed to extract table '{table_name}'")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if extractor:
            extractor.close()

if __name__ == "__main__":
    main()