#!/usr/bin/env python3
"""
Entry point for running the WordPress blog content cleaner
"""
import sys
import os
from pathlib import Path

# Add cleaner directory to path so we can import modules
cleaner_dir = Path(__file__).parent / "cleaner"
sys.path.insert(0, str(cleaner_dir))

# Change to cleaner directory so relative paths work correctly
os.chdir(cleaner_dir)

from main import main

def main_entry():
    """Entry point for the cleaner script"""
    exit(main())

if __name__ == "__main__":
    main_entry()