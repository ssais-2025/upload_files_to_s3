# AWS S3 AIS Data Uploader

A simple Python tool to upload AIS data files to Amazon S3 with automatic directory structure preservation.

## 🚀 Quick Start

### 1. Install Python
- **Windows**: Download from [python.org](https://python.org)
- **macOS**: Download from [python.org](https://python.org) or use `brew install python3`

### 2. Clone and Setup

#### Windows
```cmd
git clone https://github.com/ssais-2025/upload_files_to_s3.git
cd upload_files_to_s3

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install the tool
run.bat install

```
<details>
 <summary>macOS</summary>
    ```bash
    git clone https://github.com/ssais-2025/upload_files_to_s3.git
    cd upload_files_to_s3
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install the tool
    pip install -e .
    
    ```
</details>

### 3. Configure AWS
```bash
# Install AWS CLI
# Windows: run.bat install-aws-cli
# macOS: brew install awscli

# Configure your credentials
aws configure
```

### 4. Use the Tool

#### Windows
```cmd
# Scan your AIS data directory
run.bat ais-scan

# Upload files to S3
run.bat ais-upload

# Check status
run.bat ais-status
```
<details>
 <summary>macOS</summary>
```bash
 # Create test_data
 python create_test_data.py test_data --years 2022,2023 --months 1,2,3,4,5,6 --file-size 50
 
 # Scan your AIS data directory
 python main.py scan --base-path "/path/to/ais/data"
 
 # Upload files to S3
 python main.py upload --base-path "/tmp/upload_files_to_s3/test_data" --bucket ais-research-data-archive --region il-central-1
 
 # Check status
 python main.py status --base-path "/path/to/ais/data" --ais-research-data-archive
 ```
</details>
