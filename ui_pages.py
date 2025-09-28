"""
UI Page Classes for EasyWipe Application
Each class represents a different screen/page in the application.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QListWidget, QProgressBar, QGroupBox, QGridLayout,
    QTextEdit, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QIODevice
import os


class BasePage(QWidget):
    """Base class for all UI pages."""
    
    def __init__(self, ui_file_path: str = None):
        super().__init__()
        self.ui_file_path = ui_file_path
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI for this page."""
        if self.ui_file_path and os.path.exists(self.ui_file_path):
            self.load_ui_file()
        else:
            self.create_ui()
    
    def load_ui_file(self):
        """Load UI from .ui file."""
        loader = QUiLoader()
        ui_file = open(self.ui_file_path, 'r')
        widget = loader.load(ui_file, self)
        ui_file.close()
        
        # Set the loaded widget as the main widget
        layout = QVBoxLayout(self)
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)
    
    def create_ui(self):
        """Create UI programmatically (fallback)."""
        pass


class HomePage(BasePage):
    """Home page with main navigation."""
    
    def __init__(self):
        super().__init__("ui_files/homepage.ui")
        self.setup_connections()
    
    def setup_connections(self):
        """Setup signal connections for home page."""
        # These will be connected in the main application
        pass
    
    def create_ui(self):
        """Create home page UI programmatically."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(7)
        
        # Title
        title_label = QLabel("Easy Data Wiping :)")
        title_label.setFont(QFont("Noto Sans", 48, QFont.Bold))
        title_label.setMinimumHeight(120)
        title_label.setMaximumHeight(120)
        title_label.setAlignment(Qt.AlignBottom)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "A secure Data wiping solution.\n"
            "Permanently erases all data from your device,\n"
            "ensuring compliance with NIST SP 800-88."
        )
        desc_label.setFont(QFont("Noto Sans", 12))
        desc_label.setMinimumSize(408, 120)
        desc_label.setMaximumHeight(60)
        layout.addWidget(desc_label)
        
        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Left buttons
        left_layout = QVBoxLayout()
        
        github_button = QPushButton("Github")
        github_button.setMinimumWidth(128)
        github_button.setMaximumWidth(100)
        left_layout.addWidget(github_button)
        
        license_button = QPushButton("License")
        license_button.setMinimumWidth(128)
        license_button.setMaximumWidth(100)
        left_layout.addWidget(license_button)
        
        button_layout.addLayout(left_layout)
        button_layout.addStretch()
        
        # Right buttons
        right_layout = QVBoxLayout()
        
        laptop_button = QPushButton("Laptop/PC")
        laptop_button.setMinimumWidth(128)
        laptop_button.setMaximumWidth(100)
        right_layout.addWidget(laptop_button)
        
        android_button = QPushButton("Android")
        android_button.setMinimumWidth(128)
        android_button.setMaximumWidth(100)
        android_button.setEnabled(False)  # Disabled as per UI
        right_layout.addWidget(android_button)
        
        button_layout.addLayout(right_layout)
        
        layout.addLayout(button_layout)
        
        # Store button references
        self.laptop_button = laptop_button
        self.github_button = github_button
        self.license_button = license_button
        self.android_button = android_button


class InfoInputPage(BasePage):
    """Information input page for user and media details."""
    
    def __init__(self):
        super().__init__("ui_files/info_input_page.ui")
        self.setup_connections()
    
    def setup_connections(self):
        """Setup signal connections for info input page."""
        pass
    
    def create_ui(self):
        """Create info input page UI programmatically."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 7)
        layout.setSpacing(7)
        
        # Person Performing Sanitization Group
        person_group = QGroupBox("Person Performing Sanitization")
        person_layout = QGridLayout(person_group)
        
        # Name
        person_layout.addWidget(QLabel("Name"), 0, 0)
        self.name_edit = QLineEdit()
        person_layout.addWidget(self.name_edit, 0, 2)
        
        # Organization
        person_layout.addWidget(QLabel("Organization"), 1, 0)
        self.organization_edit = QLineEdit()
        person_layout.addWidget(self.organization_edit, 1, 2)
        
        # Title
        person_layout.addWidget(QLabel("Title"), 2, 0)
        self.title_edit = QLineEdit()
        person_layout.addWidget(self.title_edit, 2, 2)
        
        # Location
        person_layout.addWidget(QLabel("Location"), 3, 0)
        self.location_edit = QLineEdit()
        person_layout.addWidget(self.location_edit, 3, 2)
        
        # Email
        person_layout.addWidget(QLabel("Email"), 4, 0)
        self.email_edit = QLineEdit()
        person_layout.addWidget(self.email_edit, 4, 2)
        
        # Phone
        person_layout.addWidget(QLabel("Phone"), 5, 0)
        self.phone_edit = QLineEdit()
        person_layout.addWidget(self.phone_edit, 5, 2)
        
        layout.addWidget(person_group)
        
        # Media Information Group
        media_group = QGroupBox("Media Information")
        media_layout = QGridLayout(media_group)
        
        # Asset Tag
        media_layout.addWidget(QLabel("Media Property Number / Asset Tag"), 0, 0)
        self.asset_tag_edit = QLineEdit()
        media_layout.addWidget(self.asset_tag_edit, 0, 1)
        
        # Source
        media_layout.addWidget(QLabel("Source (Username / PC property no.)"), 1, 0)
        self.source_edit = QLineEdit()
        media_layout.addWidget(self.source_edit, 1, 1)
        
        # Backup Location
        media_layout.addWidget(QLabel("Backup Location"), 2, 0)
        self.backup_edit = QLineEdit()
        media_layout.addWidget(self.backup_edit, 2, 1)
        
        layout.addWidget(media_group)
        
        # Sanitization Details Group
        sanitization_group = QGroupBox("Sanitization Details")
        sanitization_layout = QGridLayout(sanitization_group)
        
        # Notes
        sanitization_layout.addWidget(QLabel("Notes"), 0, 0)
        self.notes_edit = QLineEdit()
        sanitization_layout.addWidget(self.notes_edit, 0, 1)
        
        # Destination
        sanitization_layout.addWidget(QLabel("Destination"), 1, 0)
        self.destination_edit = QLineEdit()
        sanitization_layout.addWidget(self.destination_edit, 1, 1)
        
        layout.addWidget(sanitization_group)
        
        # Continue Button
        self.continue_button = QPushButton("Continue")
        self.continue_button.setEnabled(False)  # Will be enabled when required fields are filled
        layout.addWidget(self.continue_button)


class SystemInfoPage(BasePage):
    """System information page showing available devices."""
    
    def __init__(self):
        super().__init__("ui_files/system_info_page.ui")
        self.setup_connections()
    
    def setup_connections(self):
        """Setup signal connections for system info page."""
        pass
    
    def create_ui(self):
        """Create system info page UI programmatically."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(6)
        
        # Home Button
        home_layout = QHBoxLayout()
        self.home_button = QPushButton("Home")
        self.home_button.setFont(QFont("Noto Sans", 14))
        home_layout.addWidget(self.home_button)
        home_layout.addStretch()
        layout.addLayout(home_layout)
        
        # Device List
        self.device_list = QListWidget()
        self.device_list.setFont(QFont("Noto Sans", 12))
        self.device_list.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self.device_list)
        
        # Warning
        warning_layout = QHBoxLayout()
        warning_label = QLabel("⚠️Warning: ")
        warning_label.setFont(QFont("Noto Color Emoji", 16, QFont.Bold))
        warning_label.setStyleSheet("color: rgb(246, 211, 45);")
        warning_layout.addWidget(warning_label)
        layout.addLayout(warning_layout)
        
        # Warning Text
        warning_text = QLabel(
            "All shown drives will be permanently erased.\n"
            "This action cannot be undone. Ensure backups are complete before proceeding."
        )
        warning_text.setFont(QFont("Noto Sans", 12))
        warning_text.setWordWrap(True)
        layout.addWidget(warning_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh Devices")
        self.refresh_button.setFont(QFont("Noto Sans", 14))
        button_layout.addWidget(self.refresh_button)
        
        button_layout.addStretch()
        
        self.wipe_button = QPushButton("Wipe")
        self.wipe_button.setFont(QFont("Noto Sans", 14))
        button_layout.addWidget(self.wipe_button)
        
        layout.addLayout(button_layout)


class LoadingPage(BasePage):
    """Loading page showing wipe progress."""
    
    def __init__(self):
        super().__init__("ui_files/loading_page.ui")
        self.setup_connections()
    
    def setup_connections(self):
        """Setup signal connections for loading page."""
        pass
    
    def create_ui(self):
        """Create loading page UI programmatically."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(6)
        
        # Top spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFont(QFont("Noto Sans", 12))
        self.progress_bar.setValue(24)
        layout.addWidget(self.progress_bar)
        
        # Status Label
        status_layout = QHBoxLayout()
        status_layout.addStretch()
        
        self.status_label = QLabel("In Progress....")
        self.status_label.setFont(QFont("Noto Sans", 16))
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Bottom spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))


class ReportPage(BasePage):
    """Report page showing wipe results."""
    
    def __init__(self):
        super().__init__("ui_files/report_page.ui")
        self.setup_connections()
    
    def setup_connections(self):
        """Setup signal connections for report page."""
        pass
    
    def create_ui(self):
        """Create report page UI programmatically."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(6)
        
        # Home Button
        self.home_button = QPushButton("Home")
        self.home_button.setFont(QFont("Noto Sans", 12))
        self.home_button.setMinimumWidth(100)
        layout.addWidget(self.home_button)
        
        # Success Label
        success_layout = QHBoxLayout()
        success_layout.addStretch()
        
        self.success_label = QLabel("Wiped Successful!")
        self.success_label.setFont(QFont("Noto Sans", 24, QFont.Bold))
        self.success_label.setStyleSheet("color: rgb(38, 162, 105);")
        success_layout.addWidget(self.success_label)
        
        success_layout.addStretch()
        layout.addLayout(success_layout)
        
        # Reference ID
        ref_layout = QHBoxLayout()
        ref_layout.addStretch()
        
        self.reference_label = QLabel("Ref. ID: ")
        self.reference_label.setFont(QFont("Noto Sans", 18))
        self.reference_label.setStyleSheet("color: rgb(224, 27, 36);")
        ref_layout.addWidget(self.reference_label)
        
        ref_layout.addStretch()
        layout.addLayout(ref_layout)
        
        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.verification_button = QPushButton("Verification Link")
        self.verification_button.setFont(QFont("Noto Sans", 12))
        self.verification_button.setMinimumWidth(100)
        button_layout.addWidget(self.verification_button)
        
        button_layout.addStretch()
        
        self.print_button = QPushButton("Print")
        self.print_button.setFont(QFont("Noto Sans", 12))
        self.print_button.setMinimumWidth(100)
        button_layout.addWidget(self.print_button)
        
        layout.addLayout(button_layout)
        
        # Download Button
        download_layout = QHBoxLayout()
        download_layout.addStretch()
        
        self.download_button = QPushButton("Download")
        self.download_button.setFont(QFont("Noto Sans", 12))
        self.download_button.setMinimumWidth(100)
        download_layout.addWidget(self.download_button)
        
        layout.addLayout(download_layout)


class UnsuccessfulPage(BasePage):
    """Unsuccessful wipe page."""
    
    def __init__(self):
        super().__init__("ui_files/unsucessful.ui")
        self.setup_connections()
    
    def setup_connections(self):
        """Setup signal connections for unsuccessful page."""
        pass
    
    def create_ui(self):
        """Create unsuccessful page UI programmatically."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(7)
        
        # Top spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Error Label
        error_layout = QHBoxLayout()
        error_layout.addStretch()
        
        self.error_label = QLabel("Wipe Unsuccessful")
        self.error_label.setFont(QFont("Noto Sans", 36))
        self.error_label.setStyleSheet("color: rgb(224, 27, 36);")
        error_layout.addWidget(self.error_label)
        
        error_layout.addStretch()
        layout.addLayout(error_layout)
        
        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Retry Button
        retry_layout = QHBoxLayout()
        retry_layout.addStretch()
        
        self.retry_button = QPushButton("Retry")
        retry_layout.addWidget(self.retry_button)
        
        retry_layout.addStretch()
        layout.addLayout(retry_layout)
        
        # Bottom spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
