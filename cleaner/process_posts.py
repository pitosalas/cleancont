#!/usr/bin/env python3
"""
Main processor to convert WordPress posts to markdown files with front matter
"""
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import unicodedata

from html_to_markdown import html_to_markdown, extract_excerpt
from yaml_utils import create_safe_front_matter, sanitize_filename

def slugify(text):
    """Convert text to a URL-friendly slug"""
    if not text:
        return "untitled"
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Convert to lowercase and replace spaces/special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text or "untitled"

def extract_categories(post):
    """Extract category names from post - placeholder for now"""
    categories = post.get('categories', [])
    if categories:
        return categories[0] if isinstance(categories[0], str) else str(categories[0])
    return "uncategorized"

def extract_tags(post):
    """Extract tag names from post - placeholder for now"""
    tags = post.get('tags', [])
    if tags:
        return [str(tag) for tag in tags]
    return []

def create_front_matter(post, markdown_content):
    """Create YAML front matter for the post"""
    title = post.get('title', {}).get('rendered', '').strip()
    if not title:
        title = "Untitled"
    
    # Extract subtitle from content if available (first line after title)
    subtitle = ""
    lines = markdown_content.split('\n')
    for line in lines[:3]:  # Check first few lines
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 10:
            subtitle = line[:100] + "..." if len(line) > 100 else line
            break
    
    date_str = post.get('date', '')
    if date_str:
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime('%Y-%m-%d')
        except:
            formatted_date = date_str[:10]  # Just take YYYY-MM-DD part
    else:
        formatted_date = ""
    
    category = extract_categories(post)
    tags = extract_tags(post)
    wordpress_id = post.get('id', '')
    
    return create_safe_front_matter(
        title=title,
        subtitle=subtitle,
        category=category,
        tags=tags,
        date=formatted_date,
        post_type="wp",
        wordpress_id=wordpress_id
    )

def process_post_content(post):
    """Process a single post and return markdown content"""
    html_content = post.get('content', {}).get('rendered', '')
    
    if not html_content or not html_content.strip():
        return None
    
    # Convert HTML to markdown
    markdown_content = html_to_markdown(html_content)
    
    if not markdown_content or len(markdown_content.strip()) < 10:
        return None
    
    # Create front matter
    front_matter = create_front_matter(post, markdown_content)
    
    # Combine front matter and content
    full_content = front_matter + markdown_content
    
    return full_content

def create_filename(post):
    """Create a filename for the markdown file in format: date-title.md"""
    # Get date
    date_str = post.get('date', '')
    date_prefix = ""
    if date_str:
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            date_prefix = date_obj.strftime('%Y-%m-%d')
        except:
            date_prefix = date_str[:10] if len(date_str) >= 10 else "unknown-date"
    else:
        date_prefix = "unknown-date"
    
    # Get title and create slug
    title = post.get('title', {}).get('rendered', '')
    title_slug = slugify(title) if title else "untitled"
    
    # Create filename as date-title.md
    filename = f"{date_prefix}-{title_slug}.md"
    
    # Apply filename sanitization
    return sanitize_filename(filename)

def process_all_posts(input_file, output_dir):
    """Process all posts from JSON file to markdown files"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Remove existing markdown files to regenerate clean
    for md_file in output_path.glob('*.md'):
        md_file.unlink()
    print("Removed existing markdown files for clean regeneration")
    
    # Load posts
    with open(input_file, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    processed_count = 0
    skipped_count = 0
    
    for post in posts:
        try:
            # Process the post content
            markdown_content = process_post_content(post)
            
            if not markdown_content:
                skipped_count += 1
                continue
            
            # Create filename
            filename = create_filename(post)
            
            # Handle filename conflicts
            file_path = output_path / filename
            counter = 1
            original_filename = filename
            while file_path.exists():
                name_part = original_filename.replace('.md', '')
                filename = f"{name_part}-{counter}.md"
                file_path = output_path / filename
                counter += 1
            
            # Write the markdown file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            processed_count += 1
            
            if processed_count % 100 == 0:
                print(f"Processed {processed_count} posts...")
        
        except Exception as e:
            print(f"Error processing post {post.get('id', 'unknown')}: {e}")
            skipped_count += 1
    
    print(f"\nProcessing complete!")
    print(f"Processed: {processed_count} posts")
    print(f"Skipped: {skipped_count} posts")
    print(f"Output directory: {output_path}")

def main():
    """Main entry point"""
    # Use clean posts if available, otherwise use original
    clean_posts_path = Path('../output/clean_posts.json')
    original_posts_path = Path('../json/wp_posts.json')
    
    if clean_posts_path.exists():
        input_file = clean_posts_path
        print("Using deduplicated posts...")
    else:
        input_file = original_posts_path
        print("Using original posts (run deduplicate.py first for better results)...")
    
    output_dir = Path('../output')
    
    process_all_posts(input_file, output_dir)

if __name__ == "__main__":
    main()