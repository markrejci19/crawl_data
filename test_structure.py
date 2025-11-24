#!/usr/bin/env python3
"""
Test script to validate the SBV crawler structure and imports
"""
import sys
import os

# Add the repository root to Python path
repo_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, repo_root)

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from modules.common.browser import init_driver
        print("✓ Browser module import successful")
        
        # Test that init_driver function exists and is callable
        assert callable(init_driver), "init_driver should be callable"
        print("✓ init_driver function is callable")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Other error: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    required_files = [
        "modules/__init__.py",
        "modules/common/__init__.py", 
        "modules/common/browser.py",
        "scrapers/sbv/sbv_crawler.py",
        "requirements.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(repo_root, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("Testing SBV Crawler Structure...")
    print("=" * 40)
    
    structure_ok = test_file_structure()
    print()
    
    import_ok = test_imports()
    print()
    
    if structure_ok and import_ok:
        print("✓ All tests passed! The crawler structure is ready.")
        return 0
    else:
        print("✗ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())