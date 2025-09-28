#!/usr/bin/env python3
"""
EasyWipe Launcher Script
This script handles platform-specific requirements and launches the application.
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def check_privileges():
    """Check if running with sufficient privileges."""
    if platform.system() == "Linux":
        return os.geteuid() == 0
    elif platform.system() == "Windows":
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    return False

def check_dependencies():
    """Check if required system dependencies are available."""
    missing_deps = []
    
    if platform.system() == "Linux":
        required_commands = ['shred', 'lsblk']
        optional_commands = ['hdparm', 'nvme']
        
        for cmd in required_commands:
            if subprocess.run(['which', cmd], capture_output=True).returncode != 0:
                missing_deps.append(cmd)
        
        for cmd in optional_commands:
            if subprocess.run(['which', cmd], capture_output=True).returncode != 0:
                print(f"Warning: {cmd} not found. Some features may not work.")
    
    return missing_deps

def main():
    """Main launcher function."""
    print("EasyWipe - Secure Data Wiping Application")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    
    # Check privileges
    if not check_privileges():
        print("Error: This application requires root/administrator privileges.")
        print("Please run with sudo (Linux) or as Administrator (Windows).")
        sys.exit(1)
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"Error: Missing required dependencies: {', '.join(missing_deps)}")
        print("Please install the missing tools and try again.")
        sys.exit(1)
    
    # Import and run main application
    try:
        from main import main as app_main
        app_main()
    except ImportError as e:
        print(f"Error importing application: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
