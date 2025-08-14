#!/usr/bin/env python3
"""
Main entry point for AIS data operations.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ais_cli import ais_cli

if __name__ == '__main__':
    ais_cli()
