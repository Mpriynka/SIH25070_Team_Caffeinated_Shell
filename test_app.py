#!/usr/bin/env python3
"""
Test script for EasyWipe application.
This script tests the basic functionality without requiring a full GUI environment.
"""

import sys
import os
import json
import subprocess
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import PySide6
        print("✓ PySide6 imported successfully")
    except ImportError:
        print("✗ PySide6 not available - install with: pip install PySide6")
        return False
    
    try:
        from main import DataWiper
        print("✓ DataWiper class imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import DataWiper: {e}")
        return False
    
    try:
        from ui_pages import HomePage, InfoInputPage, SystemInfoPage
        print("✓ UI page classes imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import UI pages: {e}")
        return False
    
    return True

def test_data_wiper():
    """Test DataWiper functionality."""
    print("\nTesting DataWiper...")
    
    try:
        from main import DataWiper
        wiper = DataWiper()
        
        # Test device detection
        devices = wiper.get_available_devices()
        print(f"✓ Found {len(devices)} storage devices")
        
        for device in devices[:3]:  # Show first 3 devices
            print(f"  - {device['name']}: {device['size']} ({device['type']})")
        
        return True
        
    except Exception as e:
        print(f"✗ DataWiper test failed: {e}")
        return False

def test_ui_files():
    """Test if UI files exist and are readable."""
    print("\nTesting UI files...")
    
    ui_files = [
        "ui_files/homepage.ui",
        "ui_files/info_input_page.ui",
        "ui_files/system_info_page.ui",
        "ui_files/loading_page.ui",
        "ui_files/report_page.ui",
        "ui_files/unsucessful.ui"
    ]
    
    all_exist = True
    for ui_file in ui_files:
        if os.path.exists(ui_file):
            print(f"✓ {ui_file} exists")
        else:
            print(f"✗ {ui_file} missing")
            all_exist = False
    
    return all_exist

def test_system_commands():
    """Test if required system commands are available."""
    print("\nTesting system commands...")
    
    commands = {
        'shred': 'Required for data wiping',
        'lsblk': 'Required for device detection',
        'hdparm': 'Optional - for hardware secure erase',
        'nvme': 'Optional - for NVMe devices'
    }
    
    all_available = True
    for cmd, desc in commands.items():
        try:
            result = subprocess.run(['which', cmd], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {cmd} available - {desc}")
            else:
                if cmd in ['shred', 'lsblk']:
                    print(f"✗ {cmd} missing - {desc}")
                    all_available = False
                else:
                    print(f"⚠ {cmd} missing - {desc}")
        except Exception as e:
            print(f"✗ Error checking {cmd}: {e}")
            all_available = False
    
    return all_available

def main():
    """Run all tests."""
    print("EasyWipe Application Test Suite")
    print("=" * 40)
    
    tests = [
        ("UI Files", test_ui_files),
        ("System Commands", test_system_commands),
        ("Imports", test_imports),
        ("DataWiper", test_data_wiper),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 20)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("✓ All tests passed! Application should work correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
