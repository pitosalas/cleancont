#!/usr/bin/env python3
"""
Main entry point for the cleaner package
Run the full pipeline: deduplicate -> process to markdown
"""
import sys
import json
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from deduplicate import load_posts, find_duplicates, save_deduplication_report, save_clean_posts
from process_posts import process_all_posts
from compare_posts import load_wp_posts, find_rain_posts
from process_rain_posts import main as rain_main

def collect_statistics():
    """Collect and display comprehensive statistics"""
    stats = {}
    
    # 1. Total entries in wp_posts.json
    json_path = Path('../json/wp_posts.json')
    if json_path.exists():
        original_posts = load_posts(json_path)
        stats['total_wp_posts_json'] = len(original_posts)
    else:
        stats['total_wp_posts_json'] = 0
    
    # 2. Total entries in posts folder
    posts_dir = Path('../posts')
    if posts_dir.exists():
        md_files = list(posts_dir.glob('*.md'))
        stats['total_posts_folder'] = len(md_files)
    else:
        stats['total_posts_folder'] = 0
    
    # 3. Check if rain posts list exists to get raindrop stats
    rain_list_path = Path('../output/rain_posts_list.json')
    if rain_list_path.exists():
        with open(rain_list_path, 'r', encoding='utf-8') as f:
            rain_data = json.load(f)
        stats['total_raindrops_found'] = len(rain_data)
    else:
        stats['total_raindrops_found'] = 0
    
    # 4. Check deduplication report for duplicates removed
    dedup_report_path = Path('../output/deduplication_report.json')
    if dedup_report_path.exists():
        with open(dedup_report_path, 'r', encoding='utf-8') as f:
            dedup_data = json.load(f)
        stats['duplicates_removed'] = dedup_data.get('total_duplicates', 0)
    else:
        stats['duplicates_removed'] = 0
    
    # 5. Count final blog posts generated
    output_dir = Path('../output')
    if output_dir.exists():
        wp_posts = len(list(output_dir.glob('*-wp-*.md'))) + len([f for f in output_dir.glob('*.md') if f.stem != 'README'])
        
        # Count WordPress posts by checking front matter type
        wp_count = 0
        rain_count = 0
        
        for md_file in output_dir.glob('*.md'):
            if md_file.name in ['README.md', 'CLAUDE.md']:
                continue
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'type: "wp"' in content:
                    wp_count += 1
                elif 'type: "rain"' in content:
                    rain_count += 1
            except:
                continue
        
        stats['final_wp_posts'] = wp_count
        stats['final_rain_posts'] = rain_count
        stats['final_total_posts'] = wp_count + rain_count
    else:
        stats['final_wp_posts'] = 0
        stats['final_rain_posts'] = 0
        stats['final_total_posts'] = 0
    
    return stats

def collect_wp_only_statistics():
    """Collect statistics for WordPress-only processing"""
    stats = {}
    
    # 1. Total entries in wp_posts.json
    json_path = Path('../json/wp_posts.json')
    if json_path.exists():
        original_posts = load_posts(json_path)
        stats['total_wp_posts_json'] = len(original_posts)
    else:
        stats['total_wp_posts_json'] = 0
    
    # 2. Check deduplication report for duplicates removed
    dedup_report_path = Path('../output/deduplication_report.json')
    if dedup_report_path.exists():
        with open(dedup_report_path, 'r', encoding='utf-8') as f:
            dedup_data = json.load(f)
        stats['duplicates_removed'] = dedup_data.get('total_duplicates', 0)
    else:
        stats['duplicates_removed'] = 0
    
    # 3. Count final WordPress posts generated
    output_dir = Path('../output')
    if output_dir.exists():
        wp_count = 0
        
        for md_file in output_dir.glob('*.md'):
            if md_file.name in ['README.md', 'CLAUDE.md']:
                continue
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'type: "wp"' in content:
                    wp_count += 1
            except:
                continue
        
        stats['final_wp_posts'] = wp_count
    else:
        stats['final_wp_posts'] = 0
    
    return stats

def print_wp_only_statistics(stats):
    """Print WordPress-only statistics"""
    print("\n" + "="*50)
    print("📊 WORDPRESS PROCESSING STATISTICS")
    print("="*50)
    print(f"📁 Total entries in wp_posts.json:    {stats['total_wp_posts_json']:,}")
    print(f"🗑️  Total duplicates removed:          {stats['duplicates_removed']:,}")
    print(f"📝 Final WordPress posts generated:   {stats['final_wp_posts']:,}")
    print("="*50)

def print_statistics(stats):
    """Print comprehensive statistics"""
    print("\n" + "="*60)
    print("📊 FINAL STATISTICS")
    print("="*60)
    print(f"📁 Total entries in wp_posts.json:     {stats['total_wp_posts_json']:,}")
    print(f"📂 Total entries in posts/ folder:     {stats['total_posts_folder']:,}")
    print(f"💧 Total raindrop entries found:       {stats['total_raindrops_found']:,}")
    print(f"🗑️  Total duplicates removed:           {stats['duplicates_removed']:,}")
    print("-" * 60)
    print(f"📝 Final WordPress posts generated:    {stats['final_wp_posts']:,}")
    print(f"🌧️  Final raindrop posts generated:     {stats['final_rain_posts']:,}")
    print(f"🎯 FINAL TOTAL BLOG POSTS GENERATED:   {stats['final_total_posts']:,}")
    print("="*60)

def main():
    """Run the complete cleaning pipeline with statistics"""
    print("=== WordPress Blog Content Cleaner ===\n")
    print("📋 Default mode: Processing wp_posts.json only")
    print("💡 To include posts/ folder, use --include-rain flag\n")
    
    # Step 1: Deduplication
    print("Step 1: Deduplicating WordPress posts...")
    try:
        json_path = Path('../json/wp_posts.json')
        output_path = Path('../output')
        output_path.mkdir(exist_ok=True)
        
        print("Loading posts...")
        posts = load_posts(json_path)
        print(f"Loaded {len(posts)} posts")
        
        print("Finding duplicates...")
        unique_posts, duplicates = find_duplicates(posts)
        
        print(f"Found {len(duplicates)} duplicates")
        print(f"Keeping {len(unique_posts)} unique posts")
        
        save_deduplication_report(duplicates, output_path)
        save_clean_posts(unique_posts, output_path)
        
        print("✓ WordPress deduplication complete\n")
    except Exception as e:
        print(f"✗ Deduplication failed: {e}")
        return 1
    
    # Step 2: WordPress to markdown
    print("Step 2: Converting WordPress posts to markdown...")
    try:
        clean_posts_path = Path('../output/clean_posts.json')
        original_posts_path = Path('../json/wp_posts.json')
        
        if clean_posts_path.exists():
            input_file = clean_posts_path
            print("Using deduplicated posts...")
        else:
            input_file = original_posts_path
            print("Using original posts...")
        
        output_dir = Path('../output')
        process_all_posts(input_file, output_dir)
        print("✓ WordPress markdown conversion complete\n")
    except Exception as e:
        print(f"✗ WordPress markdown conversion failed: {e}")
        return 1
    
    print("🎉 WordPress processing complete!")
    print("📁 Check the 'output' directory for results.")
    print("📝 All posts have type: 'wp'")
    
    # Collect and display statistics (WordPress only)
    stats = collect_wp_only_statistics()
    print_wp_only_statistics(stats)
    
    return 0

def main_with_rain():
    """Run the complete cleaning pipeline including rain posts"""
    print("=== WordPress Blog Content Cleaner ===\n")
    print("📋 Full mode: Processing wp_posts.json + posts/ folder\n")
    
    # Step 1: Deduplication
    print("Step 1: Deduplicating WordPress posts...")
    try:
        json_path = Path('../json/wp_posts.json')
        output_path = Path('../output')
        output_path.mkdir(exist_ok=True)
        
        print("Loading posts...")
        posts = load_posts(json_path)
        print(f"Loaded {len(posts)} posts")
        
        print("Finding duplicates...")
        unique_posts, duplicates = find_duplicates(posts)
        
        print(f"Found {len(duplicates)} duplicates")
        print(f"Keeping {len(unique_posts)} unique posts")
        
        save_deduplication_report(duplicates, output_path)
        save_clean_posts(unique_posts, output_path)
        
        print("✓ WordPress deduplication complete\n")
    except Exception as e:
        print(f"✗ Deduplication failed: {e}")
        return 1
    
    # Step 2: WordPress to markdown
    print("Step 2: Converting WordPress posts to markdown...")
    try:
        clean_posts_path = Path('../output/clean_posts.json')
        original_posts_path = Path('../json/wp_posts.json')
        
        if clean_posts_path.exists():
            input_file = clean_posts_path
            print("Using deduplicated posts...")
        else:
            input_file = original_posts_path
            print("Using original posts...")
        
        output_dir = Path('../output')
        process_all_posts(input_file, output_dir)
        print("✓ WordPress markdown conversion complete\n")
    except Exception as e:
        print(f"✗ WordPress markdown conversion failed: {e}")
        return 1
    
    # Step 3: Find rain posts
    print("Step 3: Finding rain posts...")
    try:
        json_path = Path('../json/wp_posts.json')
        wp_titles, wp_slugs = load_wp_posts(json_path)
        
        print(f"Found {len(wp_titles)} WordPress titles")
        print(f"Found {len(wp_slugs)} WordPress slugs")
        
        posts_dir = Path('../posts')
        rain_posts = find_rain_posts(posts_dir, wp_titles, wp_slugs)
        
        print(f"\nFound {len(rain_posts)} posts in posts/ directory that are NOT in WordPress JSON:")
        print("These will be added to output/ with type: 'rain'\n")
        
        for post in rain_posts[:10]:  # Show first 10
            print(f"  {post['filename']}")
        
        if len(rain_posts) > 10:
            print(f"  ... and {len(rain_posts) - 10} more")
        
        # Save the list for processing
        rain_list_path = Path('../output/rain_posts_list.json')
        with open(rain_list_path, 'w', encoding='utf-8') as f:
            json.dump(rain_posts, f, indent=2, ensure_ascii=False)
        
        print(f"\nRain posts list saved to: {rain_list_path}")
        print("✓ Rain post analysis complete\n")
    except Exception as e:
        print(f"✗ Rain post analysis failed: {e}")
        return 1
    
    # Step 4: Process rain posts
    print("Step 4: Processing rain posts...")
    try:
        rain_main()
        print("✓ Rain post processing complete\n")
    except Exception as e:
        print(f"✗ Rain post processing failed: {e}")
        return 1
    
    print("🎉 All processing complete!")
    print("📁 Check the 'output' directory for results.")
    print("📝 WordPress posts have type: 'wp'")
    print("🌧️ Rain posts have type: 'rain'")
    
    # Collect and display statistics (full mode)
    stats = collect_statistics()
    print_statistics(stats)
    
    return 0

if __name__ == "__main__":
    exit(main())