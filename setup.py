#!/usr/bin/env python3
"""
Setup script for EasyWipe application.
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    return "EasyWipe - Secure Data Wiping Application"

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="easywipe",
    version="1.0.0",
    description="A secure, cross-platform data wiping application",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="EasyWipe Team",
    author_email="team@easywipe.com",
    url="https://github.com/your-org/easywipe",
    packages=find_packages(),
    py_modules=["main", "ui_pages"],
    install_requires=read_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
    ],
    entry_points={
        "console_scripts": [
            "easywipe=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["ui_files/*.ui"],
    },
    keywords="data-wiping, security, nist, sanitization, disk-erase",
    project_urls={
        "Bug Reports": "https://github.com/your-org/easywipe/issues",
        "Source": "https://github.com/your-org/easywipe",
        "Documentation": "https://github.com/your-org/easywipe/wiki",
    },
)
