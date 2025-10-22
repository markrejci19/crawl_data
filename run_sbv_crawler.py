#!/usr/bin/env python3
"""
Main script to run SBV data crawler
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the SBV crawler"""
    try:
        from scrapers.sbv.sbv_crawler import run
        print("Starting SBV data crawler...")
        result = run()
        if result:
            print(f"Crawler completed successfully. Website: {result}")
        else:
            print("Crawler completed with errors.")
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install selenium webdriver-manager")
    except Exception as e:
        print(f"Error running crawler: {e}")

if __name__ == "__main__":
    main()