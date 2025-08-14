#!/usr/bin/env python3
"""
Setup script for S3 uploader package (local development only).
"""

from setuptools import setup, find_packages

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="s3-uploader",
    version="1.0.0",
    description="AWS S3 Large File Uploader with multipart support and progress tracking",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
)
