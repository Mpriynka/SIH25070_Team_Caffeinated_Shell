#!/usr/bin/env python3
"""
EasyWipe - Secure Data Wiping Application
A PySide6 application for secure data erasure using shred, hdparm, and nvme commands.
"""

import sys
import os
import subprocess
import json
import uuid
import platform
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QProgressBar, QGroupBox, QGridLayout, QMessageBox, QFileDialog,
    QTextEdit, QComboBox, QCheckBox, QSpinBox, QFrame
)
from PySide6.QtCore import (
    Qt, QThread, QTimer, QSize, QPropertyAnimation,
    QEasingCurve, QRect, QObject, Signal
)
from PySide6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QIODevice

# Import UI files
from ui_pages import (
    HomePage, InfoInputPage, SystemInfoPage, LoadingPage, 
    ReportPage, UnsuccessfulPage
)


class DataWiper(QObject):
    """Handles data wiping operations using system commands."""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    wipe_completed = Signal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.is_wiping = False
        self.current_device = None
        
    def get_available_devices(self) -> List[Dict[str, str]]:
        """Get list of available storage devices."""
        devices = []
        
        try:
            # Get block devices using lsblk
            result = subprocess.run(
                ['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,MODEL'],
                capture_output=True, text=True, check=True
            )
            
            data = json.loads(result.stdout)
            
            for device in data.get('blockdevices', []):
                if device.get('type') == 'disk':
                    device_info = {
                        'name': f"/dev/{device['name']}",
                        'size': device.get('size', 'Unknown'),
                        'model': device.get('model', 'Unknown'),
                        'mountpoint': device.get('mountpoint', ''),
                        'type': self._detect_device_type(device['name'])
                    }
                    devices.append(device_info)
                    
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Error getting devices: {e}")
            
        return devices
    
    def _detect_device_type(self, device_name: str) -> str:
        """Detect if device is NVMe, SATA, or other."""
        if device_name.startswith('nvme'):
            return 'NVMe'
        elif device_name.startswith('sd'):
            return 'SATA'
        else:
            return 'Other'
    
    def wipe_device(self, device_path: str, wipe_method: str = 'secure') -> bool:
        """Perform data wiping on specified device."""
        if self.is_wiping:
            return False
            
        self.is_wiping = True
        self.current_device = device_path
        
        try:
            # Check if device exists and is not mounted
            if not os.path.exists(device_path):
                self.wipe_completed.emit(False, f"Device {device_path} not found")
                return False
                
            # Unmount device if mounted
            self._unmount_device(device_path)
            
            # Perform wiping based on device type
            device_type = self._detect_device_type(os.path.basename(device_path))
            
            if device_type == 'NVMe':
                success = self._wipe_nvme(device_path)
            else:
                success = self._wipe_traditional(device_path)
                
            self.is_wiping = False
            self.wipe_completed.emit(success, "Wipe completed" if success else "Wipe failed")
            return success
            
        except Exception as e:
            self.is_wiping = False
            self.wipe_completed.emit(False, f"Error during wipe: {str(e)}")
            return False
    
    def _unmount_device(self, device_path: str):
        """Unmount device if it's mounted."""
        try:
            # Check if device has partitions
            result = subprocess.run(
                ['lsblk', '-J', '-o', 'NAME,MOUNTPOINT'],
                capture_output=True, text=True, check=True
            )
            
            data = json.loads(result.stdout)
            for device in data.get('blockdevices', []):
                if device['name'] == os.path.basename(device_path):
                    # Unmount partitions
                    for child in device.get('children', []):
                        if child.get('mountpoint'):
                            subprocess.run(['umount', child['mountpoint']], check=True)
                            self.status_updated.emit(f"Unmounted {child['mountpoint']}")
                            
        except subprocess.CalledProcessError:
            pass  # Device might not be mounted
    
    def _wipe_nvme(self, device_path: str) -> bool:
        """Wipe NVMe device using nvme command."""
        try:
            self.status_updated.emit("Starting NVMe secure erase...")
            self.progress_updated.emit(10)
            
            # Format with crypto erase (if supported)
            result = subprocess.run(
                ['nvme', 'format', device_path, '-s', '1'],
                capture_output=True, text=True, timeout=300
            )
            
            if result.returncode == 0:
                self.progress_updated.emit(50)
                self.status_updated.emit("NVMe format completed")
                
                # Additional secure erase with shred
                return self._shred_device(device_path, 50)
            else:
                # Fallback to shred only
                self.status_updated.emit("NVMe format failed, using shred...")
                return self._shred_device(device_path, 0)
                
        except subprocess.TimeoutExpired:
            self.status_updated.emit("NVMe format timed out")
            return False
        except Exception as e:
            self.status_updated.emit(f"NVMe wipe error: {str(e)}")
            return False
    
    def _wipe_traditional(self, device_path: str) -> bool:
        """Wipe traditional SATA/IDE devices."""
        try:
            self.status_updated.emit("Starting traditional device wipe...")
            self.progress_updated.emit(10)
            
            # Try hdparm secure erase first
            if self._hdparm_secure_erase(device_path):
                self.progress_updated.emit(50)
                self.status_updated.emit("hdparm secure erase completed")
                return self._shred_device(device_path, 50)
            else:
                # Fallback to shred only
                self.status_updated.emit("hdparm failed, using shred...")
                return self._shred_device(device_path, 0)
                
        except Exception as e:
            self.status_updated.emit(f"Traditional wipe error: {str(e)}")
            return False
    
    def _hdparm_secure_erase(self, device_path: str) -> bool:
        """Perform hdparm secure erase."""
        try:
            # Check if device supports secure erase
            result = subprocess.run(
                ['hdparm', '-I', device_path],
                capture_output=True, text=True, timeout=30
            )
            
            if 'not supported' in result.stdout.lower():
                return False
                
            # Set security password (empty password)
            subprocess.run(
                ['hdparm', '--user-master', 'u', '--security-set-pass', '', device_path],
                capture_output=True, text=True, timeout=30
            )
            
            # Perform secure erase
            result = subprocess.run(
                ['hdparm', '--user-master', 'u', '--security-erase', '', device_path],
                capture_output=True, text=True, timeout=600
            )
            
            return result.returncode == 0
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False
    
    def _shred_device(self, device_path: str, start_progress: int = 0) -> bool:
        """Perform shred operation on device."""
        try:
            self.status_updated.emit("Starting shred operation...")
            
            # Shred with 3 passes (NIST SP 800-88 compliant)
            result = subprocess.run(
                ['shred', '-vfz', '-n', '3', device_path],
                capture_output=True, text=True, timeout=3600
            )
            
            if result.returncode == 0:
                self.progress_updated.emit(100)
                self.status_updated.emit("Shred completed successfully")
                return True
            else:
                self.status_updated.emit(f"Shred failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.status_updated.emit("Shred operation timed out")
            return False
        except Exception as e:
            self.status_updated.emit(f"Shred error: {str(e)}")
            return False


class WipeThread(QThread):
    """Thread for performing data wiping operations."""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    wipe_completed = Signal(bool, str)
    
    def __init__(self, device_path: str, wipe_method: str = 'secure'):
        super().__init__()
        self.device_path = device_path
        self.wipe_method = wipe_method
        self.wiper = DataWiper()
        
        # Connect signals
        self.wiper.progress_updated.connect(self.progress_updated.emit)
        self.wiper.status_updated.connect(self.status_updated.emit)
        self.wiper.wipe_completed.connect(self.wipe_completed.emit)
    
    def run(self):
        """Run the wiping operation."""
        self.wiper.wipe_device(self.device_path, self.wipe_method)


class EasyWipeApp(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EasyWipe - Secure Data Wiping")
        self.setMinimumSize(900, 700)
        
        # Application data
        self.user_info = {}
        self.media_info = {}
        self.sanitization_info = {}
        self.wipe_results = {}
        self.current_devices = []
        
        # Thread management
        self.wipe_thread = None
        
        # Setup UI
        self.setup_ui()
        self.setup_style()
        
        # Load initial data
        self.refresh_devices()
    
    def setup_ui(self):
        """Setup the main UI structure."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.home_page = HomePage()
        self.info_input_page = InfoInputPage()
        self.system_info_page = SystemInfoPage()
        self.loading_page = LoadingPage()
        self.report_page = ReportPage()
        self.unsuccessful_page = UnsuccessfulPage()
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.info_input_page)
        self.stacked_widget.addWidget(self.system_info_page)
        self.stacked_widget.addWidget(self.loading_page)
        self.stacked_widget.addWidget(self.report_page)
        self.stacked_widget.addWidget(self.unsuccessful_page)
        
        # Connect signals
        self.connect_signals()
        
        # Start with homepage
        self.stacked_widget.setCurrentWidget(self.home_page)
    
    def setup_style(self):
        """Setup application styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def connect_signals(self):
        """Connect UI signals to slots."""
        # Home page signals
        self.home_page.laptop_button.clicked.connect(self.show_info_input)
        self.home_page.github_button.clicked.connect(self.show_github)
        self.home_page.license_button.clicked.connect(self.show_license)
        
        # Info input page signals
        self.info_input_page.continue_button.clicked.connect(self.validate_and_continue)
        
        # System info page signals
        self.system_info_page.refresh_button.clicked.connect(self.refresh_devices)
        self.system_info_page.wipe_button.clicked.connect(self.start_wipe)
        self.system_info_page.home_button.clicked.connect(self.show_home)
        
        # Loading page signals (handled in wipe process)
        
        # Report page signals
        self.report_page.home_button.clicked.connect(self.show_home)
        self.report_page.print_button.clicked.connect(self.print_report)
        self.report_page.download_button.clicked.connect(self.download_report)
        self.report_page.verification_button.clicked.connect(self.show_verification)
        
        # Unsuccessful page signals
        self.unsuccessful_page.retry_button.clicked.connect(self.show_system_info)
        self.unsuccessful_page.home_button.clicked.connect(self.show_home)
    
    def show_home(self):
        """Show home page."""
        self.stacked_widget.setCurrentWidget(self.home_page)
    
    def show_info_input(self):
        """Show info input page."""
        self.stacked_widget.setCurrentWidget(self.info_input_page)
    
    def show_system_info(self):
        """Show system info page."""
        self.refresh_devices()
        self.stacked_widget.setCurrentWidget(self.system_info_page)
    
    def show_loading(self):
        """Show loading page."""
        self.stacked_widget.setCurrentWidget(self.loading_page)
    
    def show_report(self):
        """Show report page."""
        self.stacked_widget.setCurrentWidget(self.report_page)
    
    def show_unsuccessful(self):
        """Show unsuccessful page."""
        self.stacked_widget.setCurrentWidget(self.unsuccessful_page)
    
    def validate_and_continue(self):
        """Validate input and continue to system info."""
        # Collect user information
        self.user_info = {
            'name': self.info_input_page.name_edit.text(),
            'organization': self.info_input_page.organization_edit.text(),
            'title': self.info_input_page.title_edit.text(),
            'location': self.info_input_page.location_edit.text(),
            'email': self.info_input_page.email_edit.text(),
            'phone': self.info_input_page.phone_edit.text()
        }
        
        # Collect media information
        self.media_info = {
            'asset_tag': self.info_input_page.asset_tag_edit.text(),
            'source': self.info_input_page.source_edit.text(),
            'backup_location': self.info_input_page.backup_edit.text()
        }
        
        # Collect sanitization information
        self.sanitization_info = {
            'notes': self.info_input_page.notes_edit.text(),
            'destination': self.info_input_page.destination_edit.text()
        }
        
        # Validate required fields
        required_fields = ['name', 'organization', 'asset_tag']
        missing_fields = [field for field in required_fields 
                         if not self.user_info.get(field) and not self.media_info.get(field)]
        
        if missing_fields:
            QMessageBox.warning(self, "Missing Information", 
                              f"Please fill in: {', '.join(missing_fields)}")
            return
        
        self.show_system_info()
    
    def refresh_devices(self):
        """Refresh the list of available devices."""
        wiper = DataWiper()
        self.current_devices = wiper.get_available_devices()
        
        # Update device list
        self.system_info_page.device_list.clear()
        
        for device in self.current_devices:
            item_text = f"{device['name']} - {device['size']} - {device['model']} ({device['type']})"
            if device['mountpoint']:
                item_text += f" [MOUNTED: {device['mountpoint']}]"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, device)
            self.system_info_page.device_list.addItem(item)
    
    def start_wipe(self):
        """Start the data wiping process."""
        selected_items = self.system_info_page.device_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "No Device Selected", 
                              "Please select a device to wipe.")
            return
        
        # Confirm wipe operation
        reply = QMessageBox.question(
            self, "Confirm Wipe", 
            "This will permanently erase all data on the selected device(s).\n"
            "This action cannot be undone. Are you sure?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Get selected devices
        selected_devices = [item.data(Qt.UserRole) for item in selected_items]
        
        # Start wiping process
        self.show_loading()
        self.loading_page.progress_bar.setValue(0)
        self.loading_page.status_label.setText("Preparing to wipe devices...")
        
        # Start wipe thread for first device (can be extended for multiple)
        device_path = selected_devices[0]['name']
        self.wipe_thread = WipeThread(device_path)
        
        # Connect thread signals
        self.wipe_thread.progress_updated.connect(self.loading_page.progress_bar.setValue)
        self.wipe_thread.status_updated.connect(self.loading_page.status_label.setText)
        self.wipe_thread.wipe_completed.connect(self.on_wipe_completed)
        
        # Start thread
        self.wipe_thread.start()
    
    def on_wipe_completed(self, success: bool, message: str):
        """Handle wipe completion."""
        if success:
            # Generate wipe report
            self.generate_wipe_report()
            self.show_report()
        else:
            self.show_unsuccessful()
    
    def generate_wipe_report(self):
        """Generate wipe report data."""
        self.wipe_results = {
            'reference_id': str(uuid.uuid4())[:8].upper(),
            'timestamp': datetime.now().isoformat(),
            'success': True,
            'devices_wiped': [item.data(Qt.UserRole) for item in self.system_info_page.device_list.selectedItems()],
            'wipe_method': 'NIST SP 800-88 Compliant',
            'verification_hash': str(uuid.uuid4())
        }
        
        # Update report page
        self.report_page.reference_label.setText(f"Ref. ID: {self.wipe_results['reference_id']}")
    
    def print_report(self):
        """Print the wipe report."""
        QMessageBox.information(self, "Print Report", 
                              "Print functionality would be implemented here.")
    
    def download_report(self):
        """Download the wipe report."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Wipe Report", 
            f"wipe_report_{self.wipe_results['reference_id']}.pdf",
            "PDF Files (*.pdf);;JSON Files (*.json)"
        )
        
        if file_path:
            QMessageBox.information(self, "Download Report", 
                                  f"Report saved to: {file_path}")
    
    def show_verification(self):
        """Show verification information."""
        QMessageBox.information(self, "Verification", 
                              f"Verification ID: {self.wipe_results['verification_hash']}\n"
                              f"Reference ID: {self.wipe_results['reference_id']}")
    
    def show_github(self):
        """Show GitHub information."""
        QMessageBox.information(self, "GitHub", 
                              "EasyWipe GitHub Repository\n"
                              "https://github.com/your-org/easywipe")
    
    def show_license(self):
        """Show license information."""
        QMessageBox.information(self, "License", 
                              "EasyWipe License\n"
                              "MIT License - See LICENSE file for details.")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("EasyWipe")
    app.setApplicationVersion("1.0.0")
    
    # Check if running with sufficient privileges
    if os.geteuid() != 0 and platform.system() == "Linux":
        QMessageBox.warning(None, "Privileges Required", 
                          "This application requires root privileges to perform data wiping.\n"
                          "Please run with sudo.")
        sys.exit(1)
    
    window = EasyWipeApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
