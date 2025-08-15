#!/usr/bin/env python3
"""
Main entry point for AIS data operations.
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from ais_cli import ais_cli
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're in the project directory and have activated the virtual environment.")
    print("Try: source venv/bin/activate")
    sys.exit(1)

if __name__ == '__main__':
    ais_cli()
