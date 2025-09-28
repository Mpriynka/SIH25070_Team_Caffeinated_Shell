#!/bin/bash
# EasyWipe Dependencies Installation Script for Ubuntu/Debian

echo "EasyWipe - Installing Dependencies"
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Update package list
echo "Updating package list..."
apt update

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Install system tools
echo "Installing system tools..."
apt install -y \
    coreutils \
    util-linux \
    hdparm \
    nvme-cli \
    python3-pip \
    python3-venv

# Verify installation
echo "Verifying installation..."
echo "Python version: $(python3 --version)"
echo "Pip version: $(pip3 --version)"

# Check required commands
echo "Checking required commands:"
for cmd in shred lsblk hdparm nvme; do
    if command -v $cmd &> /dev/null; then
        echo "✓ $cmd is available"
    else
        echo "✗ $cmd is missing"
    fi
done

echo ""
echo "Installation complete!"
echo "Run the application with: sudo python3 main.py"
