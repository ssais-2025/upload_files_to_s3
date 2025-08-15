"""
AWS utilities for S3 operations - combines configuration and S3 client.
"""

import os
import boto3
import botocore
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, Dict, Any, List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import Field


class S3Config(BaseSettings):
    """S3 configuration settings."""
    
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_default_region: str = Field("us-east-1", env="AWS_DEFAULT_REGION")
    
    s3_bucket_name: Optional[str] = Field(None, env="S3_BUCKET_NAME")
    s3_endpoint_url: str = Field("https://s3.amazonaws.com", env="S3_ENDPOINT_URL")
    
    max_concurrent_parts: int = Field(10, env="MAX_CONCURRENT_PARTS")
    part_size_mb: int = Field(100, env="PART_SIZE_MB")
    max_retries: int = Field(3, env="MAX_RETRIES")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class S3Client:
    """S3 client wrapper with error handling and configuration."""
    
    def __init__(self, 
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 region_name: Optional[str] = None,
                 endpoint_url: Optional[str] = None):
        """Initialize S3 client."""
        self.config = S3Config()
        self.aws_access_key_id = aws_access_key_id or self.config.aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key or self.config.aws_secret_access_key
        self.region_name = region_name or self.config.aws_default_region
        self.endpoint_url = endpoint_url or self.config.s3_endpoint_url
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the boto3 S3 client."""
        try:
            session = boto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            self.client = session.client(
                's3',
                endpoint_url=self.endpoint_url,
                config=botocore.config.Config(
                    retries=dict(max_attempts=self.config.max_retries)
                )
            )
            
        except NoCredentialsError:
            raise Exception("AWS credentials not found. Please configure your credentials.")
        except Exception as e:
            raise Exception(f"Failed to initialize S3 client: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test S3 connection by listing buckets."""
        try:
            self.client.list_buckets()
            return True
        except ClientError as e:
            print(f"Failed to connect to S3: {e}")
            return False
    
    def bucket_exists(self, bucket_name: str) -> bool:
        """Check if a bucket exists."""
        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return False
            raise e
    
    def get_bucket_location(self, bucket_name: str) -> str:
        """Get the region of a bucket."""
        try:
            response = self.client.get_bucket_location(Bucket=bucket_name)
            return response.get('LocationConstraint') or 'us-east-1'
        except ClientError as e:
            raise Exception(f"Failed to get bucket location: {e}")
    
    def list_objects(self, bucket_name: str, prefix: str = "", max_keys: int = 1000) -> list:
        """List objects in a bucket with optional prefix."""
        try:
            response = self.client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            return response.get('Contents', [])
        except ClientError as e:
            raise Exception(f"Failed to list objects: {e}")


# Global configuration instance
config = S3Config()
