"""
Specialized AIS data uploader for S3 with YEAR/MONTH structure support.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from tqdm import tqdm

from aws import S3Client
from uploader import S3Uploader, AISFileScanner

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AISUploader:
    """Specialized uploader for AIS data files."""
    
    def __init__(self, base_path: str, bucket_name: str, 
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 region_name: Optional[str] = None):
        """
        Initialize AIS uploader.
        
        Args:
            base_path: Base directory path for AIS data
            bucket_name: S3 bucket name
            aws_access_key_id: AWS access key
            aws_secret_access_key: AWS secret key
            region_name: AWS region
        """
        self.base_path = Path(base_path)
        self.bucket_name = bucket_name
        
        # Initialize S3 components
        self.s3_client = S3Client(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        self.uploader = S3Uploader(self.s3_client)
        
        # Initialize file scanner
        self.scanner = AISFileScanner(base_path)
        
        # Upload progress tracking
        self.upload_progress_file = "ais_upload_progress.json"
        self.uploaded_files = self._load_upload_progress()
        
        logger.info(f"Initialized AIS uploader for bucket: {bucket_name}")
    
    def _load_upload_progress(self) -> Dict:
        """Load upload progress from disk."""
        try:
            if os.path.exists(self.upload_progress_file):
                with open(self.upload_progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load upload progress: {e}")
        
        return {}
    
    def _save_upload_progress(self):
        """Save upload progress to disk."""
        try:
            with open(self.upload_progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.uploaded_files, f, indent=2, ensure_ascii=False)
            logger.debug("Upload progress saved")
        except Exception as e:
            logger.error(f"Error saving upload progress: {e}")
    
    def _is_file_uploaded(self, file_info: Dict) -> bool:
        """
        Check if a file has already been uploaded.
        
        Args:
            file_info: File information dictionary
            
        Returns:
            True if file is already uploaded, False otherwise
        """
        file_path = file_info['filepath']
        
        if file_path not in self.uploaded_files:
            return False
        
        # Check if file size matches (basic validation)
        if os.path.exists(file_path):
            current_size = os.path.getsize(file_path)
            uploaded_size = self.uploaded_files[file_path].get('size', 0)
            return current_size == uploaded_size
        
        return False
    
    def _mark_file_uploaded(self, file_info: Dict, s3_etag: str):
        """
        Mark a file as successfully uploaded.
        
        Args:
            file_info: File information dictionary
            s3_etag: S3 ETag from successful upload
        """
        file_path = file_info['filepath']
        
        self.uploaded_files[file_path] = {
            'filename': file_info['filename'],
            's3_key': file_info['s3_key'],
            'size': file_info['size'],
            'upload_time': datetime.now().isoformat(),
            's3_etag': s3_etag,
            'year': file_info['year'],
            'month': file_info['month']
        }
        
        self._save_upload_progress()
        logger.info(f"Marked file as uploaded: {file_info['filename']}")
    
    def _get_upload_queue(self) -> List[Dict]:
        """
        Get the queue of files that need to be uploaded.
        
        Returns:
            List of files to upload
        """
        # Run scan phase
        files_data, upload_queue = self.scanner.run_scan_phase()
        
        # Filter out already uploaded files
        pending_uploads = []
        for file_info in upload_queue:
            if not self._is_file_uploaded(file_info):
                pending_uploads.append(file_info)
            else:
                logger.debug(f"Skipping already uploaded file: {file_info['filename']}")
        
        logger.info(f"Upload queue prepared: {len(pending_uploads)} files pending")
        return pending_uploads
    
    def upload_file(self, file_info: Dict, progress_callback: Optional[Callable] = None) -> bool:
        """
        Upload a single AIS file to S3.
        
        Args:
            file_info: File information dictionary
            progress_callback: Optional progress callback function
            
        Returns:
            True if upload successful, False otherwise
        """
        file_path = file_info['filepath']
        s3_key = file_info['s3_key']
        
        logger.info(f"Uploading: {file_info['filename']} -> s3://{self.bucket_name}/{s3_key}")
        
        try:
            # Validate file exists and integrity
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            # Check if file was modified since last upload
            if self._is_file_uploaded(file_info):
                current_size = os.path.getsize(file_path)
                uploaded_size = self.uploaded_files[file_path].get('size', 0)
                
                if current_size != uploaded_size:
                    logger.warning(f"File size changed since last upload: {file_path}")
                    logger.warning(f"Previous: {uploaded_size}, Current: {current_size}")
                else:
                    logger.info(f"File already uploaded and unchanged: {file_info['filename']}")
                    return True
            
            # Upload to S3
            success = self.uploader.upload_file(
                file_path=file_path,
                bucket_name=self.bucket_name,
                object_key=s3_key,
                progress_callback=progress_callback
            )
            
            if success:
                # Get S3 ETag for tracking
                try:
                    response = self.s3_client.client.head_object(
                        Bucket=self.bucket_name,
                        Key=s3_key
                    )
                    s3_etag = response.get('ETag', '').strip('"')
                except Exception as e:
                    logger.warning(f"Could not get S3 ETag: {e}")
                    s3_etag = ""
                
                # Mark as uploaded
                self._mark_file_uploaded(file_info, s3_etag)
                logger.info(f"Successfully uploaded: {file_info['filename']}")
                return True
            else:
                logger.error(f"Upload failed: {file_info['filename']}")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading {file_info['filename']}: {e}")
            return False
    
    def upload_all_files(self, max_files: Optional[int] = None, 
                         progress_callback: Optional[Callable] = None) -> Dict:
        """
        Upload all pending AIS files to S3.
        
        Args:
            max_files: Maximum number of files to upload (None for all)
            progress_callback: Optional progress callback function
            
        Returns:
            Dictionary with upload results
        """
        logger.info("=== PHASE 2: File Upload ===")
        
        # Get upload queue
        upload_queue = self._get_upload_queue()
        
        if not upload_queue:
            logger.info("No files to upload")
            return {
                'total_files': 0,
                'uploaded': 0,
                'failed': 0,
                'skipped': 0
            }
        
        # Limit files if specified
        if max_files:
            upload_queue = upload_queue[:max_files]
            logger.info(f"Limited upload to {max_files} files")
        
        total_files = len(upload_queue)
        uploaded = 0
        failed = 0
        skipped = 0
        
        logger.info(f"Starting upload of {total_files} files...")
        
        # Create progress bar
        with tqdm(total=total_files, desc="Uploading AIS files", unit="file") as pbar:
            for i, file_info in enumerate(upload_queue):
                pbar.set_description(f"Uploading {file_info['filename']}")
                
                # Check if file was already uploaded during this session
                if self._is_file_uploaded(file_info):
                    logger.debug(f"Skipping already uploaded file: {file_info['filename']}")
                    skipped += 1
                    pbar.update(1)
                    continue
                
                # Upload file
                if self.upload_file(file_info, progress_callback):
                    uploaded += 1
                else:
                    failed += 1
                
                pbar.update(1)
                
                # Update progress bar description
                pbar.set_postfix({
                    'Uploaded': uploaded,
                    'Failed': failed,
                    'Skipped': skipped
                })
        
        # Log summary
        logger.info("=== Upload Summary ===")
        logger.info(f"Total files: {total_files}")
        logger.info(f"Successfully uploaded: {uploaded}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Skipped: {skipped}")
        
        return {
            'total_files': total_files,
            'uploaded': uploaded,
            'failed': failed,
            'skipped': skipped
        }
    
    def resume_upload(self) -> Dict:
        """
        Resume upload from where it left off.
        
        Returns:
            Dictionary with upload results
        """
        logger.info("Resuming upload from previous session...")
        return self.upload_all_files()
    
    def get_upload_status(self) -> Dict:
        """
        Get current upload status.
        
        Returns:
            Dictionary with upload status information
        """
        total_files = len(self.uploaded_files)
        
        # Group by year/month
        by_period = {}
        for file_path, info in self.uploaded_files.items():
            year = info.get('year', 'unknown')
            month = info.get('month', 'unknown')
            
            if year not in by_period:
                by_period[year] = {}
            if month not in by_period[year]:
                by_period[year][month] = []
            
            by_period[year][month].append({
                'filename': info['filename'],
                'size': info['size'],
                'upload_time': info['upload_time']
            })
        
        return {
            'total_uploaded': total_files,
            'by_period': by_period,
            'uploaded_files': self.uploaded_files
        }
    
    def validate_uploaded_files(self) -> Dict:
        """
        Validate that uploaded files still exist and match S3.
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Validating uploaded files...")
        
        validation_results = {
            'total': len(self.uploaded_files),
            'valid': 0,
            'invalid': 0,
            'missing': 0,
            'errors': []
        }
        
        for file_path, info in self.uploaded_files.items():
            try:
                # Check if local file exists
                if not os.path.exists(file_path):
                    validation_results['missing'] += 1
                    validation_results['errors'].append(f"Local file missing: {file_path}")
                    continue
                
                # Check if S3 object exists
                try:
                    response = self.s3_client.client.head_object(
                        Bucket=self.bucket_name,
                        Key=info['s3_key']
                    )
                    
                    # Compare sizes
                    local_size = os.path.getsize(file_path)
                    s3_size = response.get('ContentLength', 0)
                    
                    if local_size == s3_size:
                        validation_results['valid'] += 1
                    else:
                        validation_results['invalid'] += 1
                        validation_results['errors'].append(
                            f"Size mismatch for {file_path}: Local={local_size}, S3={s3_size}"
                        )
                        
                except Exception as e:
                    validation_results['invalid'] += 1
                    validation_results['errors'].append(f"S3 object not found: {info['s3_key']} - {e}")
                    
            except Exception as e:
                validation_results['invalid'] += 1
                validation_results['errors'].append(f"Validation error for {file_path}: {e}")
        
        logger.info(f"Validation completed: {validation_results['valid']} valid, "
                   f"{validation_results['invalid']} invalid, {validation_results['missing']} missing")
        
        return validation_results
