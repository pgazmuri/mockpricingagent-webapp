#!/usr/bin/env python3
"""
Test script to verify the Mock Pricing Agent web application functionality.
"""

import requests
import time
import sys

def test_web_server():
    """Test if the web server is running and responding."""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✓ Web server is running and responding")
            return True
        else:
            print(f"✗ Web server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to connect to web server: {e}")
        return False

def test_terminal_page():
    """Test if the terminal page is accessible."""
    try:
        response = requests.get('http://localhost:5000/terminal', timeout=5)
        if response.status_code == 200:
            print("✓ Terminal page is accessible")
            return True
        else:
            print(f"✗ Terminal page responded with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to access terminal page: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Mock Pricing Agent Web Application")
    print("=" * 50)
    
    tests = [
        test_web_server,
        test_terminal_page,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The application is ready to use.")
        return 0
    else:
        print("✗ Some tests failed. Please check the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
