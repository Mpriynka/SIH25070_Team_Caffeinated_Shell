# EasyWipe - Secure Data Wiping Application

A secure, cross-platform data wiping application designed to permanently erase data from storage devices while ensuring compliance with NIST SP 800-88 standards.

## Features

- **Secure Data Erasure**: Uses industry-standard tools (shred, hdparm, nvme) for comprehensive data wiping
- **NIST SP 800-88 Compliant**: Follows established standards for data sanitization
- **Cross-Platform Support**: Works on Linux and Windows systems
- **User-Friendly Interface**: Intuitive PySide6-based GUI
- **Device Detection**: Automatically detects and lists available storage devices
- **Progress Tracking**: Real-time progress updates during wiping operations
- **Audit Trail**: Generates tamper-proof certificates and reports
- **Multiple Wipe Methods**: Supports different wiping techniques based on device type

## Supported Devices

- **NVMe SSDs**: Uses nvme format with crypto erase
- **SATA/IDE Drives**: Uses hdparm secure erase + shred
- **All Storage Devices**: Fallback to shred for comprehensive wiping

## Installation

### Prerequisites

- Python 3.8 or higher
- Linux or Windows operating system
- Root/Administrator privileges (required for data wiping operations)

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/your-org/easywipe.git
cd easywipe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
sudo python main.py  # Linux
# or
python main.py       # Windows (run as Administrator)
```

### Install as Package

```bash
pip install easywipe
sudo easywipe  # Linux
```

## Usage

1. **Launch the Application**: Run with appropriate privileges
2. **Enter Information**: Fill in user and media details
3. **Select Devices**: Choose storage devices to wipe
4. **Confirm Wipe**: Review and confirm the wiping operation
5. **Monitor Progress**: Watch real-time progress updates
6. **Download Report**: Save the wipe certificate and report

## Security Features

- **Tamper-Proof Certificates**: Digitally signed wipe certificates
- **Verification Hashes**: Unique identifiers for wipe verification
- **Audit Logging**: Complete audit trail of wiping operations
- **Secure Erasure**: Multiple overwrite passes for complete data destruction

## Technical Details

### Wiping Methods

1. **NVMe Devices**:
   - `nvme format -s 1` (crypto erase)
   - `shred -vfz -n 3` (3-pass overwrite)

2. **Traditional Drives**:
   - `hdparm --security-erase` (hardware secure erase)
   - `shred -vfz -n 3` (3-pass overwrite)

3. **Fallback Method**:
   - `shred -vfz -n 3` (3-pass overwrite for all devices)

### System Requirements

- **Linux**: Requires `shred`, `hdparm`, `nvme-cli`, `lsblk`
- **Windows**: Requires Windows 10/11 with appropriate drivers
- **Memory**: Minimum 512MB RAM
- **Storage**: 100MB for application files

## Development

### Project Structure

```
easywipe/
├── main.py              # Main application entry point
├── ui_pages.py          # UI page classes
├── ui_files/            # Qt Designer UI files
│   ├── homepage.ui
│   ├── info_input_page.ui
│   ├── system_info_page.ui
│   ├── loading_page.ui
│   ├── report_page.ui
│   └── unsucessful.ui
├── requirements.txt     # Python dependencies
├── setup.py            # Package setup
└── README.md           # This file
```

### Building from Source

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Build package
python setup.py sdist bdist_wheel
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

**WARNING**: This software permanently erases data from storage devices. This action cannot be undone. Always ensure you have proper backups before using this software. The authors are not responsible for any data loss.

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## Roadmap

- [ ] Android device support
- [ ] Network storage wiping
- [ ] Batch wiping operations
- [ ] Custom wipe patterns
- [ ] Integration with asset management systems
- [ ] Cloud-based certificate verification

## Acknowledgments

- NIST for SP 800-88 guidelines
- Qt/PySide6 for the GUI framework
- Linux kernel developers for storage tools
- Open source community for various utilities
