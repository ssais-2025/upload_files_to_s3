"""
Command-line interface for AIS data operations.
"""

import os
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
import json

from ais_uploader import AISUploader
from uploader import AISFileScanner

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def ais_cli():
    """AIS Data Uploader - Upload AIS data files to S3 with YEAR/MONTH structure."""
    pass


@ais_cli.command()
@click.option('--bucket', '-b', required=True, help='S3 bucket name')
@click.option('--region', '-r', help='AWS region')
@click.option('--access-key', help='AWS access key ID')
@click.option('--secret-key', help='AWS secret access key')
def test(bucket, region, access_key, secret_key):
    """Test S3 connection and bucket access."""
    try:
        from aws import S3Client
        
        # Clean bucket name (remove s3:// prefix if present)
        clean_bucket = bucket.replace('s3://', '')
        
        console.print("🔍 Testing S3 connection...", style="blue")
        
        # Initialize S3 client
        s3_client = S3Client(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Test basic connection
        if s3_client.test_connection():
            console.print("✅ S3 connection successful!", style="green")
        else:
            console.print("❌ S3 connection failed!", style="red")
            return
        
        # Test bucket access
        console.print(f"🔍 Checking bucket '{clean_bucket}'...", style="blue")
        if s3_client.bucket_exists(clean_bucket):
            console.print(f"✅ Bucket '{clean_bucket}' exists and is accessible!", style="green")
            
            # Get bucket region
            try:
                bucket_region = s3_client.get_bucket_location(clean_bucket)
                console.print(f"📍 Bucket region: {bucket_region}", style="cyan")
            except Exception as e:
                console.print(f"⚠️  Could not determine bucket region: {e}", style="yellow")
        else:
            console.print(f"❌ Bucket '{clean_bucket}' does not exist or is not accessible!", style="red")
            return
        
        console.print("🎉 All tests passed! S3 is ready for uploads.", style="green")
        
    except Exception as e:
        # Escape any special characters that might cause Rich markup errors
        error_msg = str(e).replace('[', '\\[').replace(']', '\\]').replace(':', '\\:')
        console.print(f"❌ Error: {error_msg}", style="red")


@ais_cli.command()
@click.option('--base-path', '-p', required=True, 
              help='Base directory path (e.g., "E:\\AISDData\\exactEarth")')
@click.option('--bucket', '-b', required=True, help='S3 bucket name')
@click.option('--region', '-r', help='AWS region')
@click.option('--access-key', help='AWS access key ID')
@click.option('--secret-key', help='AWS secret access key')
@click.option('--max-files', type=int, help='Maximum number of files to upload')
@click.option('--resume', is_flag=True, help='Resume upload from previous session')
def upload(base_path, bucket, region, access_key, secret_key, max_files, resume):
    """Upload AIS data files to S3."""
    try:
        # Clean bucket name (remove s3:// prefix if present)
        clean_bucket = bucket.replace('s3://', '')
        
        # Initialize AIS uploader
        uploader = AISUploader(
            base_path=base_path,
            bucket_name=clean_bucket,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Test S3 connection
        if not uploader.s3_client.test_connection():
            console.print("❌ S3 connection failed!", style="red")
            return
        
        # Check if bucket exists
        if not uploader.s3_client.bucket_exists(clean_bucket):
            console.print(f"❌ Bucket '{clean_bucket}' does not exist!", style="red")
            return
        
        if resume:
            console.print("🔄 Resuming upload from previous session...", style="yellow")
            results = uploader.resume_upload()
        else:
            console.print("🚀 Starting AIS data upload...", style="green")
            results = uploader.upload_all_files(max_files=max_files)
        
        # Display results
        display_upload_results(results)
        
    except Exception as e:
        # Escape any special characters that might cause Rich markup errors
        error_msg = str(e).replace('[', '\\[').replace(']', '\\]').replace(':', '\\:')
        console.print(f"❌ Error: {error_msg}", style="red")


@ais_cli.command()
@click.option('--base-path', '-p', required=True, 
              help='Base directory path (e.g., "E:\\AISDData\\exactEarth")')
@click.option('--output', '-o', default='ais_files.json', 
              help='Output file for file list')
def scan(base_path, output):
    """Scan AIS data directory and generate file list."""
    try:
        console.print(f"🔍 Scanning AIS data directory: {base_path}", style="blue")
        
        # Initialize scanner
        scanner = AISFileScanner(base_path, output)
        
        # Run scan phase
        files_data, upload_queue = scanner.run_scan_phase()
        
        # Display scan results
        display_scan_results(files_data, upload_queue)
        
        console.print(f"✅ Scan completed. File list saved to: {output}", style="green")
        
    except Exception as e:
        # Escape any special characters that might cause Rich markup errors
        error_msg = str(e).replace('[', '\\[').replace(']', '\\]').replace(':', '\\:')
        console.print(f"❌ Error: {error_msg}", style="red")


@ais_cli.command()
@click.option('--base-path', '-p', required=True, 
              help='Base directory path (e.g., "E:\\AISDData\\exactEarth")')
@click.option('--bucket', '-b', required=True, help='S3 bucket name')
@click.option('--region', '-r', help='AWS region')
@click.option('--access-key', help='AWS access key ID')
@click.option('--secret-key', help='AWS secret access key')
def status(base_path, bucket, region, access_key, secret_key):
    """Show upload status and statistics."""
    try:
        # Clean bucket name (remove s3:// prefix if present)
        clean_bucket = bucket.replace('s3://', '')
        
        # Initialize AIS uploader
        uploader = AISUploader(
            base_path=base_path,
            bucket_name=clean_bucket,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Get status
        status_info = uploader.get_upload_status()
        
        # Display status
        display_status(status_info)
        
    except Exception as e:
        # Escape any special characters that might cause Rich markup errors
        error_msg = str(e).replace('[', '\\[').replace(']', '\\]').replace(':', '\\:')
        console.print(f"❌ Error: {error_msg}", style="red")


@ais_cli.command()
@click.option('--base-path', '-p', required=True, 
              help='Base directory path (e.g., "E:\\AISDData\\exactEarth")')
@click.option('--bucket', '-b', required=True, help='S3 bucket name')
@click.option('--region', '-r', help='AWS region')
@click.option('--access-key', help='AWS access key ID')
@click.option('--secret-key', help='AWS secret access key')
def validate(base_path, bucket, region, access_key, secret_key):
    """Validate uploaded files against S3."""
    try:
        console.print("🔍 Validating uploaded files...", style="blue")
        
        # Clean bucket name (remove s3:// prefix if present)
        clean_bucket = bucket.replace('s3://', '')
        
        # Initialize AIS uploader
        uploader = AISUploader(
            base_path=base_path,
            bucket_name=clean_bucket,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Run validation
        validation_results = uploader.validate_uploaded_files()
        
        # Display validation results
        display_validation_results(validation_results)
        
    except Exception as e:
        # Escape any special characters that might cause Rich markup errors
        error_msg = str(e).replace('[', '\\[').replace(']', '\\]').replace(':', '\\:')
        console.print(f"❌ Error: {error_msg}", style="red")


@ais_cli.command()
@click.option('--base-path', '-p', required=True, 
              help='Base directory path (e.g., "E:\\AISDData\\exactEarth")')
@click.option('--bucket', '-b', required=True, help='S3 bucket name')
@click.option('--region', '-r', help='AWS region')
@click.option('--access-key', help='AWS access key ID')
@click.option('--secret-key', help='AWS secret access key')
def info(base_path, bucket, region, access_key, secret_key):
    """Show detailed information about AIS data and upload status."""
    try:
        console.print("📊 AIS Data Information", style="blue")
        console.print("=" * 50)
        
        # Clean bucket name (remove s3:// prefix if present)
        clean_bucket = bucket.replace('s3://', '')
        
        # Initialize components
        scanner = AISFileScanner(base_path)
        uploader = AISUploader(
            base_path=base_path,
            bucket_name=clean_bucket,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Get file information
        files_data, upload_queue = scanner.run_scan_phase()
        status_info = uploader.get_upload_status()
        
        # Display comprehensive information
        display_comprehensive_info(files_data, upload_queue, status_info, clean_bucket)
        
    except Exception as e:
        # Escape any special characters that might cause Rich markup errors
        error_msg = str(e).replace('[', '\\[').replace(']', '\\]').replace(':', '\\:')
        console.print(f"❌ Error: {error_msg}", style="red")


def display_upload_results(results):
    """Display upload results in a formatted table."""
    table = Table(title="Upload Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Files", str(results['total_files']))
    table.add_row("Successfully Uploaded", str(results['uploaded']))
    table.add_row("Failed", str(results['failed']))
    table.add_row("Skipped", str(results['skipped']))
    
    console.print(table)
    
    if results['failed'] > 0:
        console.print("⚠️  Some files failed to upload. Check logs for details.", style="yellow")
    elif results['uploaded'] > 0:
        console.print("✅ Upload completed successfully!", style="green")


def display_scan_results(files_data, upload_queue):
    """Display scan results in a formatted table."""
    # Count files by year/month
    total_files = 0
    by_period = {}
    
    for year, months in files_data.items():
        by_period[year] = {}
        for month, files in months.items():
            by_period[year][month] = len(files)
            total_files += len(files)
    
    # Create summary table
    summary_table = Table(title="Scan Summary")
    summary_table.add_column("Year", style="cyan")
    summary_table.add_column("Month", style="magenta")
    summary_table.add_column("Files", style="green")
    
    for year in sorted(by_period.keys()):
        for month in sorted(by_period[year].keys()):
            summary_table.add_row(year, month, str(by_period[year][month]))
    
    console.print(summary_table)
    console.print(f"Total files found: {total_files}", style="green")
    console.print(f"Files ready for upload: {len(upload_queue)}", style="blue")


def display_status(status_info):
    """Display upload status in a formatted table."""
    table = Table(title="Upload Status")
    table.add_column("Year", style="cyan")
    table.add_column("Month", style="magenta")
    table.add_column("Files Uploaded", style="green")
    table.add_column("Total Size", style="yellow")
    
    total_files = status_info['total_uploaded']
    total_size = 0
    
    for year in sorted(status_info['by_period'].keys()):
        for month in sorted(status_info['by_period'][year].keys()):
            files = status_info['by_period'][year][month]
            month_size = sum(f['size'] for f in files)
            total_size += month_size
            
            table.add_row(
                year,
                month,
                str(len(files)),
                f"{month_size / (1024*1024*1024):.2f} GB"
            )
    
    console.print(table)
    console.print(f"Total files uploaded: {total_files}", style="green")
    console.print(f"Total size uploaded: {total_size / (1024*1024*1024):.2f} GB", style="green")


def display_validation_results(validation_results):
    """Display validation results in a formatted table."""
    table = Table(title="Validation Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Files", str(validation_results['total']))
    table.add_row("Valid", str(validation_results['valid']))
    table.add_row("Invalid", str(validation_results['invalid']))
    table.add_row("Missing", str(validation_results['missing']))
    
    console.print(table)
    
    if validation_results['errors']:
        console.print("⚠️  Validation Errors:", style="yellow")
        for error in validation_results['errors'][:10]:  # Show first 10 errors
            console.print(f"  • {error}", style="red")
        
        if len(validation_results['errors']) > 10:
            console.print(f"  ... and {len(validation_results['errors']) - 10} more errors", style="yellow")


def display_comprehensive_info(files_data, upload_queue, status_info, bucket):
    """Display comprehensive information about AIS data."""
    # File discovery summary
    total_discovered = sum(
        len(files) for months in files_data.values() 
        for files in months.values()
    )
    
    # Upload status summary
    total_uploaded = status_info['total_uploaded']
    
    # Create summary panel
    summary_text = Text()
    summary_text.append(f"Base Path: {os.path.abspath('.')}\n", style="cyan")
    summary_text.append(f"S3 Bucket: {bucket}\n", style="cyan")
    summary_text.append(f"Files Discovered: {total_discovered}\n", style="green")
    summary_text.append(f"Files Uploaded: {total_uploaded}\n", style="green")
    summary_text.append(f"Files Pending: {len(upload_queue)}", style="yellow")
    
    summary_panel = Panel(summary_text, title="Summary", border_style="blue")
    console.print(summary_panel)
    
    # Year/Month breakdown
    if files_data:
        breakdown_table = Table(title="Files by Year/Month")
        breakdown_table.add_column("Year", style="cyan")
        breakdown_table.add_column("Month", style="magenta")
        breakdown_table.add_column("Total Files", style="green")
        breakdown_table.add_column("Uploaded", style="blue")
        breakdown_table.add_column("Pending", style="yellow")
        
        for year in sorted(files_data.keys()):
            for month in sorted(files_data[year].keys()):
                total_files = len(files_data[year][month])
                uploaded = len(status_info['by_period'].get(year, {}).get(month, []))
                pending = total_files - uploaded
                
                breakdown_table.add_row(year, month, str(total_files), str(uploaded), str(pending))
        
        console.print(breakdown_table)


if __name__ == '__main__':
    ais_cli()
