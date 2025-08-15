#!/usr/bin/env python3
"""
Test Data Generator for AIS Uploader

This script creates a test file hierarchy with YEAR/MONTH structure
and generates dummy RAR files to test the AIS uploader functionality.

Usage:
    python create_test_data.py [output_directory] [--files-per-month N] [--years Y] [--months M]

Examples:
    python create_test_data.py test_data
    python create_test_data.py test_data --files-per-month 5 --years 2022,2023 --months 1,2,3,4,5,6
"""

import os
import sys
import argparse
import random
from pathlib import Path
from datetime import datetime
import zipfile
import tempfile
import shutil


def create_dummy_rar_file(file_path, size_mb=1):
    """
    Create a dummy RAR file (actually a ZIP file with .rar extension for testing).
    
    Args:
        file_path: Path where to create the file
        size_mb: Size in MB (default 1MB)
    """
    # Create a temporary directory for the dummy content
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some dummy files to compress
        dummy_file = os.path.join(temp_dir, "dummy.txt")
        
        # Calculate how many bytes we need for the target size
        target_bytes = size_mb * 1024 * 1024
        
        # Since we're using ZIP_STORED (no compression), we need exactly the target size
        # Each line is about 80 bytes, so calculate lines needed
        line_size = 80
        lines_needed = target_bytes // line_size
        
        # Create varied content to reach the target size
        content_lines = []
        for i in range(lines_needed):
            # Create varied content
            line = f"AIS Data Test File #{i:06d} - Sample data for testing. "
            line += f"Timestamp: {datetime.now().isoformat()} - Random: {random.randint(100000, 999999)}\n"
            content_lines.append(line)
        
        content = "".join(content_lines)
        
        # Trim to exact target size
        if len(content) > target_bytes:
            content = content[:target_bytes]
        elif len(content) < target_bytes:
            # Pad with additional content if too short
            padding = "A" * (target_bytes - len(content))
            content += padding
        
        with open(dummy_file, 'w') as f:
            f.write(content)
        
        # Create a ZIP file with no compression to maintain size
        with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_STORED) as zipf:
            zipf.write(dummy_file, os.path.basename(dummy_file))
        
        # Verify the final file size is close to target
        final_size = file_path.stat().st_size
        size_diff = abs(final_size - target_bytes) / target_bytes
        
        if size_diff > 0.1:  # If more than 10% difference
            print(f"    Warning: Target size was {size_mb}MB, actual size is {final_size / (1024*1024):.1f}MB")


def create_test_hierarchy(base_path, years, months, files_per_month, file_size_mb=1):
    """
    Create the test file hierarchy.
    
    Args:
        base_path: Base directory to create the hierarchy in
        years: List of years to create
        months: List of months to create
        files_per_month: Number of files to create per month
        file_size_mb: Size of each file in MB
    """
    base_path = Path(base_path)
    
    print(f"Creating test data in: {base_path.absolute()}")
    print(f"Years: {years}")
    print(f"Months: {months}")
    print(f"Files per month: {files_per_month}")
    print(f"File size: {file_size_mb}MB")
    print("-" * 50)
    
    total_files = 0
    total_size = 0
    
    for year in years:
        year_path = base_path / str(year)
        year_path.mkdir(parents=True, exist_ok=True)
        
        for month in months:
            month_path = year_path / f"{month:02d}"
            month_path.mkdir(parents=True, exist_ok=True)
            
            print(f"Creating {month_path}...")
            
            for file_num in range(1, files_per_month + 1):
                # Create filename with timestamp and random data
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                random_suffix = random.randint(1000, 9999)
                filename = f"ais_data_{timestamp}_{random_suffix}.rar"
                file_path = month_path / filename
                
                # Create the dummy RAR file
                create_dummy_rar_file(file_path, file_size_mb)
                
                file_size = file_path.stat().st_size
                total_files += 1
                total_size += file_size
                
                print(f"  Created: {filename} ({file_size / (1024*1024):.1f}MB)")
    
    print("-" * 50)
    print(f"Total files created: {total_files}")
    print(f"Total size: {total_size / (1024*1024*1024):.2f}GB")
    print(f"Test data ready in: {base_path.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="Create test data hierarchy for AIS uploader testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_test_data.py test_data
  python create_test_data.py test_data --files-per-month 3
  python create_test_data.py test_data --years 2022,2023 --months 1,2,3,4,5,6
  python create_test_data.py test_data --files-per-month 5 --file-size 2
        """
    )
    
    parser.add_argument(
        "output_dir",
        help="Output directory for test data"
    )
    
    parser.add_argument(
        "--files-per-month",
        type=int,
        default=3,
        help="Number of files to create per month (default: 3)"
    )
    
    parser.add_argument(
        "--years",
        default="2022,2023,2024",
        help="Comma-separated list of years (default: 2022,2023,2024)"
    )
    
    parser.add_argument(
        "--months",
        default="1,2,3,4,5,6,7,8,9,10,11,12",
        help="Comma-separated list of months (default: 1,2,3,4,5,6,7,8,9,10,11,12)"
    )
    
    parser.add_argument(
        "--file-size",
        type=int,
        default=1,
        help="Size of each file in MB (default: 1)"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean existing output directory before creating new data"
    )
    
    args = parser.parse_args()
    
    # Parse years and months
    try:
        years = [int(y.strip()) for y in args.years.split(",")]
        months = [int(m.strip()) for m in args.months.split(",")]
    except ValueError as e:
        print(f"Error parsing years or months: {e}")
        sys.exit(1)
    
    # Validate inputs
    if not (1 <= min(months) <= max(months) <= 12):
        print("Error: Months must be between 1 and 12")
        sys.exit(1)
    
    if args.files_per_month < 1:
        print("Error: Files per month must be at least 1")
        sys.exit(1)
    
    if args.file_size < 1:
        print("Error: File size must be at least 1MB")
        sys.exit(1)
    
    output_dir = Path(args.output_dir)
    
    # Clean existing directory if requested
    if args.clean and output_dir.exists():
        print(f"Cleaning existing directory: {output_dir}")
        shutil.rmtree(output_dir)
    
    # Create the test hierarchy
    try:
        create_test_hierarchy(
            output_dir,
            years,
            months,
            args.files_per_month,
            args.file_size
        )
        
        print("\n✅ Test data created successfully!")
        print(f"\nYou can now test your AIS uploader with:")
        print(f"  run.bat ais-scan")
        print(f"  run.bat ais-upload")
        print(f"\nOr manually:")
        print(f"  python main.py scan --base-path \"{output_dir.absolute()}\"")
        print(f"  python main.py upload --base-path \"{output_dir.absolute()}\" --bucket your-bucket")
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
