#!/usr/bin/env python3
"""
Process posts from posts/ directory that are not in WordPress JSON
Add them to output/ with type: 'rain'
"""
import json
import re
from pathlib import Path
from datetime import datetime
from html import unescape
from yaml_utils import create_safe_front_matter, sanitize_filename

def extract_front_matter_and_content(file_path):
    """Extract existing front matter and content from a markdown file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has front matter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            front_matter = parts[1].strip()
            body_content = parts[2].strip()
            return front_matter, body_content
    
    # No front matter, treat entire content as body
    return "", content.strip()

def parse_title_from_filename(filename):
    """Extract title from filename like '2004-01-04-Title-Here.md'"""
    # Remove .md extension
    name = filename.replace('.md', '')
    
    # Split by date pattern
    parts = name.split('-', 3)  # Split into year, month, day, title
    if len(parts) >= 4:
        title_part = parts[3]
        # Replace hyphens with spaces
        title = title_part.replace('-', ' ')
        return title
    
    return name.replace('-', ' ')

def parse_date_from_filename(filename):
    """Extract date from filename like '2004-01-04-Title-Here.md'"""
    parts = filename.split('-', 3)
    if len(parts) >= 3:
        try:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            return f"{year:04d}-{month:02d}-{day:02d}"
        except ValueError:
            pass
    
    return ""

def create_rain_front_matter(filename, existing_front_matter, body_content):
    """Create front matter for rain posts"""
    # Parse existing front matter if it exists
    existing_data = {}
    if existing_front_matter:
        for line in existing_front_matter.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                existing_data[key] = value
    
    # Extract info from filename
    title = existing_data.get('title', parse_title_from_filename(filename))
    date = existing_data.get('date', parse_date_from_filename(filename))
    
    # Extract subtitle from content (first non-empty line that's not a heading)
    subtitle = ""
    if body_content:
        lines = body_content.split('\n')
        for line in lines[:5]:  # Check first few lines
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                subtitle = line[:100] + "..." if len(line) > 100 else line
                break
    
    # Get other fields from existing front matter or defaults
    category = existing_data.get('category', 'uncategorized')
    tags = existing_data.get('tags', [])
    
    return create_safe_front_matter(
        title=title,
        subtitle=subtitle,
        category=category,
        tags=tags,
        date=date,
        post_type="rain"
    )

def process_rain_post(source_path, output_path):
    """Process a single rain post"""
    existing_front_matter, body_content = extract_front_matter_and_content(source_path)
    
    # Create new front matter with type: "rain"
    new_front_matter = create_rain_front_matter(source_path.name, existing_front_matter, body_content)
    
    # Combine front matter and content
    full_content = new_front_matter + body_content
    
    # Write to output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)

def main():
    # Load list of rain posts
    rain_list_path = Path('../output/rain_posts_list.json')
    if not rain_list_path.exists():
        print("Error: rain_posts_list.json not found. Run compare_posts.py first.")
        return
    
    with open(rain_list_path, 'r', encoding='utf-8') as f:
        rain_posts = json.load(f)
    
    output_dir = Path('../output')
    processed_count = 0
    
    print(f"Processing {len(rain_posts)} rain posts...")
    
    for post_info in rain_posts:
        source_path = Path(post_info['path'])
        filename = post_info['filename']
        
        # Apply filename sanitization
        sanitized_filename = sanitize_filename(filename)
        
        # Create output path with sanitized filename
        output_path = output_dir / sanitized_filename
        
        # Handle filename conflicts with existing files
        counter = 1
        original_filename = sanitized_filename
        while output_path.exists():
            name_part = original_filename.replace('.md', '')
            sanitized_filename = f"{name_part}-rain-{counter}.md"
            output_path = output_dir / sanitized_filename
            counter += 1
        
        try:
            process_rain_post(source_path, output_path)
            processed_count += 1
            
            if processed_count % 100 == 0:
                print(f"Processed {processed_count} rain posts...")
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    print(f"\nProcessed {processed_count} rain posts")
    print(f"Rain posts added to output directory with type: 'rain'")

if __name__ == "__main__":
    main()