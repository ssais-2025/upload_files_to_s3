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

#### macOS
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

#### macOS
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

### 💡 Virtual Environment Tips

**Always activate your virtual environment before using the tool:**
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Deactivate when done
deactivate
```

**Why use virtual environments?**
- ✅ Isolates project dependencies
- ✅ Prevents conflicts with system Python
- ✅ Easy to clean up and recreate
- ✅ Professional Python development practice

## 🖥️ Commands by Platform

### Windows Commands

#### Basic Commands
```cmd
run.bat help              # Show all commands
run.bat install           # Install the tool
run.bat install-dev       # Install with dev tools
```

#### AIS Data Commands
```cmd
run.bat ais-scan          # Scan data directory
run.bat ais-upload        # Upload to S3
run.bat ais-status        # Show upload status
run.bat ais-validate      # Validate uploaded files
run.bat ais-info          # Show detailed info
run.bat ais-resume        # Resume interrupted upload
```

#### Development Commands
```cmd
run.bat lint              # Check code quality
run.bat format            # Format code
run.bat clean             # Clean temporary files
```

### macOS Commands

#### Basic Commands
```bash
# Install package
pip install -e .
pip install -e ".[dev]"

# Show help
python main.py --help
```

#### AIS Data Commands
```bash
# Scan data directory
python main.py scan --base-path "/path/to/ais/data" --output ais_files.json

# Upload to S3
python main.py upload --base-path "/path/to/ais/data" --bucket your-bucket

# Show upload status
python main.py status --base-path "/path/to/ais/data" --bucket your-bucket

# Validate uploaded files
python main.py validate --base-path "/path/to/ais/data" --bucket your-bucket

# Show detailed info
python main.py info --base-path "/path/to/ais/data" --bucket your-bucket

# Resume interrupted upload
python main.py upload --base-path "/path/to/ais/data" --bucket your-bucket --resume
```

#### Development Commands
```bash
# Code quality
black src/
isort src/
flake8 src/
mypy src/

# Clean up
find . -type d -name __pycache__ -delete
find . -type f -name "*.pyc" -delete
```

## ⚙️ Configuration

### 1. Create `.env` file
Copy `env.example` to `.env` and edit:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=your_bucket_name

# AIS Data Path (adjust for your system)
AIS_BASE_PATH=E:\AISDData\exactEarth  # Windows
# AIS_BASE_PATH=/path/to/ais/data      # macOS
```

### 2. Adjust Paths

#### Windows
Edit `run.bat` and change these paths:
```cmd
set BASE_PATH=E:\Your\Actual\Path
set BUCKET_NAME=your-actual-bucket
```

#### macOS
Use command line arguments:
```bash
python main.py scan --base-path "/your/actual/path" --bucket your-bucket
```

## 📁 How It Works

### Phase 1: Scanning
- Scans your `YEAR/MONTH` directory structure
- Finds `.rar` files
- Calculates MD5 checksums
- Saves file list to `ais_files.json`

### Phase 2: Uploading
- Uploads files to S3 preserving `YEAR/MONTH` structure
- Tracks progress and saves upload status
- Can resume after interruptions
- Validates file integrity

## 🔧 Requirements

- **Python 3.8+**
- **AWS account** with S3 access
- **IAM permissions**: `s3:PutObject`, `s3:ListBucket`
- **AWS CLI** (installed automatically)

### Platform Support

This project works on:
- **Windows**: PowerShell 5.1+ or Command Prompt (see `run.bat` and `run.ps1`)
- **macOS**: Terminal with bash/zsh (see direct Python commands)
- **Linux**: Terminal with bash/zsh (same as macOS)

## 📖 Examples

### Basic Usage

#### Windows
```cmd
# Scan your data
run.bat ais-scan

# Upload everything
run.bat ais-upload

# Check what's uploaded
run.bat ais-status
```

#### macOS
```bash
# Scan your data
python main.py scan --base-path "/path/to/ais/data"

# Upload everything
python main.py upload --base-path "/path/to/ais/data" --bucket your-bucket

# Check what's uploaded
python main.py status --base-path "/path/to/ais/data" --bucket your-bucket
```

### Custom Paths

#### Windows
```cmd
# Use custom paths in run.bat or edit the file
run.bat ais-scan
```

#### macOS
```bash
# Use custom paths
python main.py scan --base-path "/custom/path" --output my_files.json
python main.py upload --base-path "/custom/path" --bucket my-bucket
```

### Testing with Sample Data

#### Windows
```cmd
# Create test data to try the tool
create_test.bat test_data

# Create more test files
create_test.bat test_data --files-per-month 5 --years 2022,2023

# Create larger test files
create_test.bat test_data --file-size 5 --months 1,2,3,4,5,6
```

#### macOS
```bash
# Create test data to try the tool
python create_test_data.py test_data --years 2022,2023 --months 1,2,3,4,5,6 --file-size 50
```

## 🛠️ Troubleshooting

### Common Issues

**"Module not found" errors:**
- **Windows**: `run.bat install`
- **macOS**: `pip install -e .`

**AWS connection issues:**
```bash
aws configure
# Windows: run.bat test-connection
# macOS: python main.py test
```

**Permission errors:**
- Check your IAM permissions
- Verify bucket name and region

### Getting Help

#### Windows
```cmd
# Show all available commands
run.bat help

# Show AIS tool help
run.bat ais-help

# Test S3 connection
run.bat test-connection
```

#### macOS
```bash
# Show all available commands
python main.py --help

# Show specific command help
python main.py scan --help
python main.py upload --help

# Test S3 connection
python main.py test
```

## 📁 Project Structure

```
upload_files_to_s3/
├── README.md              # This file
├── main.py                # Main program
├── run.bat                # Windows commands
├── run.ps1                # PowerShell commands (advanced)
├── create_test_data.py    # Test data generator
├── create_test.bat        # Windows test data commands
├── env.example            # Configuration template
├── requirements.txt       # Python packages needed
├── setup.py               # Installation script
└── src/                   # Source code
    ├── aws.py             # AWS configuration & S3 client
    ├── uploader.py        # File scanning & S3 uploads
    ├── ais_uploader.py    # AIS-specific logic
    └── ais_cli.py         # Command interface
```

## 🚀 Advanced Usage

### PowerShell Users (Windows)
Use `run.ps1` for more features:
```powershell
.\run.ps1 help
.\run.ps1 format
.\run.ps1 lint
```

### Direct Python (All Platforms)
```bash
python main.py --help
python main.py scan --help
python main.py upload --help
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Support

- Create an issue on GitHub
- Check the examples above
- Review your `.env` configuration
