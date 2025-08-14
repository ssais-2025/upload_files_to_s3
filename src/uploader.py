"""
Comprehensive S3 uploader with file scanning and multipart upload support.
Combines file scanning, checksum management, and S3 uploads in one module.
"""

import os
import math
import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Callable, Dict, List, Tuple
from tqdm import tqdm
import boto3
from botocore.exceptions import ClientError
from pathlib import Path
from datetime import datetime
import logging

from .aws import S3Client, config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AISFileScanner:
    """Scanner for AIS data files in YEAR/MONTH directory structure."""
    
    def __init__(self, base_path: str, file_list_path: str = "ais_files.json", 
                 checksum_path: str = "ais_checksums.json"):
        """
        Initialize the AIS file scanner.
        
        Args:
            base_path: Base directory path (e.g., "E:\\AISDData\\exactEarth")
            file_list_path: Path to store the file list
            checksum_path: Path to store file checksums
        """
        self.base_path = Path(base_path)
        self.file_list_path = Path(file_list_path)
        self.checksum_path = Path(checksum_path)
        self.files_data = {}
        self.checksums = {}
        
        # Validate base path
        if not self.base_path.exists():
            raise FileNotFoundError(f"Base path does not exist: {self.base_path}")
        
        logger.info(f"Initialized AIS scanner with base path: {self.base_path}")
    
    def scan_directory(self) -> Dict[str, List[Dict]]:
        """
        Scan the directory structure and return organized file data.
        
        Returns:
            Dictionary with YEAR/MONTH structure containing file information
        """
        logger.info("Starting directory scan...")
        
        if not self.base_path.exists():
            raise FileNotFoundError(f"Base path not found: {self.base_path}")
        
        # Initialize structure
        files_by_period = {}
        
        # Walk through the directory structure
        for year_dir in self.base_path.iterdir():
            if not year_dir.is_dir() or not year_dir.name.isdigit():
                continue
                
            year = year_dir.name
            files_by_period[year] = {}
            
            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir() or not month_dir.name.isdigit():
                    continue
                    
                month = month_dir.name.zfill(2)  # Ensure 2-digit format
                files_by_period[year][month] = []
                
                # Scan for RAR files
                for file_path in month_dir.glob("*.rar"):
                    file_info = self._get_file_info(file_path, year, month)
                    files_by_period[year][month].append(file_info)
                    logger.debug(f"Found file: {file_path}")
        
        logger.info(f"Scan completed. Found files in {len(files_by_period)} years")
        return files_by_period
    
    def _get_file_info(self, file_path: Path, year: str, month: str) -> Dict:
        """
        Get information about a single file.
        
        Args:
            file_path: Path to the file
            year: Year directory name
            month: Month directory name
            
        Returns:
            Dictionary with file information
        """
        stat = file_path.stat()
        
        return {
            'filename': file_path.name,
            'filepath': str(file_path),
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'year': year,
            'month': month,
            's3_key': f"{year}/{month}/{file_path.name}"
        }
    
    def calculate_checksums(self, files_by_period: Dict[str, List[Dict]]) -> Dict[str, str]:
        """
        Calculate MD5 checksums for all files.
        
        Args:
            files_by_period: Dictionary with YEAR/MONTH file structure
            
        Returns:
            Dictionary mapping file paths to checksums
        """
        logger.info("Calculating file checksums...")
        checksums = {}
        
        total_files = sum(len(files) for year_data in files_by_period.values() 
                         for files in year_data.values())
        
        with tqdm(total=total_files, desc="Calculating checksums") as pbar:
            for year, year_data in files_by_period.items():
                for month, files in year_data.items():
                    for file_info in files:
                        file_path = file_info['filepath']
                        checksum = self._calculate_file_checksum(file_path)
                        checksums[file_path] = checksum
                        pbar.update(1)
        
        logger.info(f"Checksums calculated for {len(checksums)} files")
        return checksums
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum for a single file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def save_file_list(self, files_by_period: Dict[str, List[Dict]]) -> None:
        """Save the file list to JSON."""
        try:
            with open(self.file_list_path, 'w') as f:
                json.dump(files_by_period, f, indent=2)
            logger.info(f"File list saved to {self.file_list_path}")
        except Exception as e:
            logger.error(f"Failed to save file list: {e}")
    
    def save_checksums(self, checksums: Dict[str, str]) -> None:
        """Save checksums to JSON."""
        try:
            with open(self.checksum_path, 'w') as f:
                json.dump(checksums, f, indent=2)
            logger.info(f"Checksums saved to {self.checksum_path}")
        except Exception as e:
            logger.error(f"Failed to save checksums: {e}")
    
    def load_file_list(self) -> Dict[str, List[Dict]]:
        """Load the file list from JSON."""
        try:
            if self.file_list_path.exists():
                with open(self.file_list_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"File list loaded from {self.file_list_path}")
                return data
            else:
                logger.info("No existing file list found")
                return {}
        except Exception as e:
            logger.error(f"Failed to load file list: {e}")
            return {}
    
    def load_checksums(self) -> Dict[str, str]:
        """Load checksums from JSON."""
        try:
            if self.checksum_path.exists():
                with open(self.checksum_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"Checksums loaded from {self.checksum_path}")
                return data
            else:
                logger.info("No existing checksums found")
                return {}
        except Exception as e:
            logger.error(f"Failed to load checksums: {e}")
            return {}


class S3Uploader:
    """Handles multipart uploads to S3 with progress tracking."""
    
    def __init__(self, s3_client: S3Client):
        """Initialize uploader with S3 client."""
        self.s3_client = s3_client
        self.client = s3_client.client
    
    def upload_file(self, 
                   file_path: str, 
                   bucket_name: str, 
                   object_key: Optional[str] = None,
                   progress_callback: Optional[Callable] = None) -> bool:
        """
        Upload a file to S3 using multipart upload for large files.
        
        Args:
            file_path: Path to the local file
            bucket_name: S3 bucket name
            object_key: S3 object key (defaults to filename)
            progress_callback: Optional callback for progress updates
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        object_key = object_key or os.path.basename(file_path)
        
        # Use multipart upload for files larger than 100MB
        if file_size > 100 * 1024 * 1024:  # 100MB
            return self._multipart_upload(file_path, bucket_name, object_key, file_size, progress_callback)
        else:
            return self._simple_upload(file_path, bucket_name, object_key, progress_callback)
    
    def _simple_upload(self, file_path: str, bucket_name: str, object_key: str, 
                       progress_callback: Optional[Callable]) -> bool:
        """Simple upload for small files."""
        try:
            with tqdm(total=os.path.getsize(file_path), unit='B', unit_scale=True, 
                     desc=f"Uploading {os.path.basename(file_path)}") as pbar:
                
                def progress_hook(bytes_transferred):
                    pbar.update(bytes_transferred)
                    if progress_callback:
                        progress_callback(bytes_transferred)
                
                self.client.upload_file(
                    file_path, 
                    bucket_name, 
                    object_key,
                    Callback=progress_hook
                )
            
            print(f"Successfully uploaded {file_path} to s3://{bucket_name}/{object_key}")
            return True
            
        except Exception as e:
            print(f"Failed to upload {file_path}: {e}")
            return False
    
    def _multipart_upload(self, file_path: str, bucket_name: str, object_key: str, 
                          file_size: int, progress_callback: Optional[Callable]) -> bool:
        """Multipart upload for large files."""
        try:
            # Calculate part size and number of parts
            part_size = config.part_size_mb * 1024 * 1024  # Convert MB to bytes
            num_parts = math.ceil(file_size / part_size)
            
            print(f"Starting multipart upload: {num_parts} parts, {part_size / (1024*1024):.1f}MB each")
            
            # Initiate multipart upload
            response = self.client.create_multipart_upload(
                Bucket=bucket_name,
                Key=object_key
            )
            upload_id = response['UploadId']
            
            # Upload parts
            parts = []
            with tqdm(total=file_size, unit='B', unit_scale=True, 
                     desc=f"Uploading {os.path.basename(file_path)}") as pbar:
                
                with ThreadPoolExecutor(max_workers=config.max_concurrent_parts) as executor:
                    futures = []
                    
                    for part_num in range(1, num_parts + 1):
                        start_byte = (part_num - 1) * part_size
                        end_byte = min(start_byte + part_size, file_size)
                        
                        future = executor.submit(
                            self._upload_part,
                            file_path, bucket_name, object_key, upload_id,
                            part_num, start_byte, end_byte
                        )
                        futures.append(future)
                    
                    # Collect results
                    for future in as_completed(futures):
                        try:
                            part_info = future.result()
                            parts.append(part_info)
                            pbar.update(part_info['Size'])
                            if progress_callback:
                                progress_callback(part_info['Size'])
                        except Exception as e:
                            print(f"Part upload failed: {e}")
                            # Abort multipart upload
                            self.client.abort_multipart_upload(
                                Bucket=bucket_name,
                                Key=object_key,
                                UploadId=upload_id
                            )
                            return False
            
            # Complete multipart upload
            self.client.complete_multipart_upload(
                Bucket=bucket_name,
                Key=object_key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            
            print(f"Successfully uploaded {file_path} to s3://{bucket_name}/{object_key}")
            return True
            
        except Exception as e:
            print(f"Failed to upload {file_path}: {e}")
            # Abort multipart upload on failure
            try:
                self.client.abort_multipart_upload(
                    Bucket=bucket_name,
                    Key=object_key,
                    UploadId=upload_id
                )
            except:
                pass
            return False
    
    def _upload_part(self, file_path: str, bucket_name: str, object_key: str, 
                     upload_id: str, part_num: int, start_byte: int, end_byte: int) -> Dict:
        """Upload a single part of a multipart upload."""
        try:
            with open(file_path, 'rb') as f:
                f.seek(start_byte)
                part_data = f.read(end_byte - start_byte)
            
            response = self.client.upload_part(
                Bucket=bucket_name,
                Key=object_key,
                PartNumber=part_num,
                UploadId=upload_id,
                Body=part_data
            )
            
            return {
                'ETag': response['ETag'],
                'PartNumber': part_num,
                'Size': end_byte - start_byte
            }
            
        except Exception as e:
            raise Exception(f"Failed to upload part {part_num}: {e}")
