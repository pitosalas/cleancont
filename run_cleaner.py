#!/usr/bin/env python3
"""
Entry point for running the WordPress blog content cleaner
"""
import sys
import os
import argparse
from pathlib import Path

# Add cleaner directory to path so we can import modules
cleaner_dir = Path(__file__).parent / "cleaner"
sys.path.insert(0, str(cleaner_dir))

# Change to cleaner directory so relative paths work correctly
os.chdir(cleaner_dir)

from main import main, main_with_rain

def main_entry():
    """Entry point for the cleaner script with argument parsing"""
    parser = argparse.ArgumentParser(
        description="WordPress Blog Content Cleaner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python run_cleaner.py                    # WordPress only (default)
  uv run python run_cleaner.py --include-rain     # WordPress + posts/ folder
        """
    )
    
    parser.add_argument(
        '--include-rain', 
        action='store_true',
        help='Include processing of posts/ folder (rain posts). Default: WordPress only.'
    )
    
    args = parser.parse_args()
    
    if args.include_rain:
        exit(main_with_rain())
    else:
        exit(main())

if __name__ == "__main__":
    main_entry()