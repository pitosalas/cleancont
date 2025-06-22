#!/usr/bin/env python3
"""
Compare posts in posts/ directory with WordPress JSON to find posts that should be added as type: 'rain'
"""
import json
from pathlib import Path
import re

def load_wp_posts(json_path):
    """Load WordPress posts and extract their titles for comparison"""
    with open(json_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    wp_titles = set()
    wp_slugs = set()
    
    for post in posts:
        title = post.get('title', {}).get('rendered', '').strip()
        slug = post.get('slug', '').strip()
        
        if title:
            # Normalize title for comparison
            normalized_title = normalize_for_comparison(title)
            wp_titles.add(normalized_title)
        
        if slug:
            wp_slugs.add(slug)
    
    return wp_titles, wp_slugs

def normalize_for_comparison(text):
    """Normalize text for comparison by removing special chars and converting to lowercase"""
    # Convert underscores to spaces first
    text = text.replace('_', ' ')
    # Remove HTML entities and special characters (but keep spaces and hyphens temporarily)
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Convert hyphens to spaces
    text = text.replace('-', ' ')
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_title_from_filename(filename):
    """Extract title from filename like '2004-01-04-Title-Here.md'"""
    # Remove .md extension
    name = filename.replace('.md', '')
    
    # Split by date pattern
    parts = name.split('-', 3)  # Split into year, month, day, title
    if len(parts) >= 4:
        title_part = parts[3]
        # Replace both hyphens and underscores with spaces
        title = title_part.replace('-', ' ').replace('_', ' ')
        return normalize_for_comparison(title)
    
    return normalize_for_comparison(name)

def find_rain_posts(posts_dir, wp_titles, wp_slugs):
    """Find posts in posts/ directory that don't appear in WordPress JSON"""
    posts_path = Path(posts_dir)
    rain_posts = []
    
    for md_file in posts_path.glob('*.md'):
        filename = md_file.name
        extracted_title = extract_title_from_filename(filename)
        
        # Check if this post exists in WordPress data
        is_wp_post = False
        
        # Check against normalized titles
        if extracted_title in wp_titles:
            is_wp_post = True
        
        # Check against slugs (remove date prefix for comparison)
        name_without_date = filename.replace('.md', '')
        parts = name_without_date.split('-', 3)
        if len(parts) >= 4:
            slug_candidate = '-'.join(parts[3:]).lower()
            if slug_candidate in wp_slugs:
                is_wp_post = True
        
        # If not found in WordPress data, it's a "rain" post
        if not is_wp_post:
            rain_posts.append({
                'filename': filename,
                'path': str(md_file),
                'extracted_title': extracted_title
            })
    
    return rain_posts

def main():
    # Load WordPress posts
    json_path = Path('../json/wp_posts.json')
    wp_titles, wp_slugs = load_wp_posts(json_path)
    
    print(f"Found {len(wp_titles)} WordPress titles")
    print(f"Found {len(wp_slugs)} WordPress slugs")
    
    # Find rain posts
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

if __name__ == "__main__":
    main()