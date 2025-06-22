#!/usr/bin/env python3
"""
Main entry point for the cleaner package
Run the full pipeline: deduplicate -> process to markdown
"""
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from deduplicate import main as deduplicate_main
from process_posts import main as process_main
from compare_posts import main as compare_main
from process_rain_posts import main as rain_main

def main():
    """Run the complete cleaning pipeline"""
    print("=== WordPress Blog Content Cleaner ===\n")
    
    print("Step 1: Deduplicating posts...")
    try:
        deduplicate_main()
        print("✓ Deduplication complete\n")
    except Exception as e:
        print(f"✗ Deduplication failed: {e}")
        return 1
    
    print("Step 2: Converting WordPress posts to markdown...")
    try:
        process_main()
        print("✓ WordPress markdown conversion complete\n")
    except Exception as e:
        print(f"✗ WordPress markdown conversion failed: {e}")
        return 1
    
    print("Step 3: Finding rain posts...")
    try:
        compare_main()
        print("✓ Rain post analysis complete\n")
    except Exception as e:
        print(f"✗ Rain post analysis failed: {e}")
        return 1
    
    print("Step 4: Processing rain posts...")
    try:
        rain_main()
        print("✓ Rain post processing complete\n")
    except Exception as e:
        print(f"✗ Rain post processing failed: {e}")
        return 1
    
    print("🎉 All processing complete!")
    print("Check the 'output' directory for results.")
    print("- WordPress posts have type: 'wp'")
    print("- Rain posts have type: 'rain'")
    return 0

if __name__ == "__main__":
    exit(main())