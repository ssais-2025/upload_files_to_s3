# AWS S3 Large File Uploader

This project provides an easy way to upload large files (including files >160 GB and up to multiple terabytes) to Amazon S3 using the AWS CLI. It supports multipart uploads and shows upload progress in the terminal.

## 🔧 Requirements

- AWS account with an S3 bucket
- IAM user with appropriate permissions (`s3:PutObject`, `s3:ListBucket`)
- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed and configured

## 🚀 Getting Started

### 1. Install AWS CLI

#### macOS
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

#### Windows
Download and install from:  
[https://awscli.amazonaws.com/AWSCLIV2.msi](https://awscli.amazonaws.com/AWSCLIV2.msi)

### 2. Configure AWS CLI

```bash
aws configure
```

Provide:
- Access Key ID
- Secret Access Key
- Default region (e.g., `us-east-1`)
- Output format (optional)

### 3. Upload a Large File

```bash
aws s3 cp /path/to/your/file.ext s3://your-bucket-name/ --expected-size 2TB
```

The CLI will automatically handle multipart upload and display a real-time progress bar.

## ✅ IAM Policy Example

Make sure your IAM user has permissions like:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

## 📁 Folder Structure (if using scripts)

```
.
├── README.md
├── upload.py         # Optional Python script for progress-enabled upload
└── requirements.txt  # tqdm, boto3 (for SDK use)
```

## 📜 License

This project is open source and available under the [MIT License](LICENSE).
