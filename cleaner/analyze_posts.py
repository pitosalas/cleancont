#!/usr/bin/env python3
"""
Analyze WordPress posts for duplicates and content patterns
"""
import json
from collections import defaultdict, Counter
from urllib.parse import urlparse

def load_posts(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_duplicates(posts):
    """Identify potential duplicates by various criteria"""
    
    # Group by title
    titles = defaultdict(list)
    for post in posts:
        title = post['title']['rendered'].strip().lower()
        titles[title].append(post)
    
    # Group by slug
    slugs = defaultdict(list)
    for post in posts:
        slugs[post['slug']].append(post)
    
    # Group by content hash (first 100 chars)
    content_hashes = defaultdict(list)
    for post in posts:
        content = post['content']['rendered'][:100].strip()
        content_hashes[content].append(post)
    
    return titles, slugs, content_hashes

def print_duplicate_report(titles, slugs, content_hashes):
    """Print analysis of duplicates"""
    
    print("=== DUPLICATE ANALYSIS ===\n")
    
    # Title duplicates
    title_dupes = {k: v for k, v in titles.items() if len(v) > 1}
    print(f"Posts with duplicate titles: {len(title_dupes)}")
    for title, posts in sorted(title_dupes.items())[:5]:  # Show first 5
        print(f"  '{title}': {len(posts)} posts")
        for post in posts:
            print(f"    ID: {post['id']}, Date: {post['date'][:10]}")
    
    print()
    
    # Slug duplicates
    slug_dupes = {k: v for k, v in slugs.items() if len(v) > 1}
    print(f"Posts with duplicate slugs: {len(slug_dupes)}")
    for slug, posts in sorted(slug_dupes.items())[:5]:
        print(f"  '{slug}': {len(posts)} posts")
    
    print()
    
    # Content duplicates
    content_dupes = {k: v for k, v in content_hashes.items() if len(v) > 1}
    print(f"Posts with duplicate content starts: {len(content_dupes)}")
    
    print()

def analyze_content_patterns(posts):
    """Analyze content patterns and quality"""
    
    content_lengths = []
    empty_content = 0
    short_content = 0  # < 100 chars
    
    for post in posts:
        content = post['content']['rendered']
        content_len = len(content.strip())
        content_lengths.append(content_len)
        
        if content_len == 0:
            empty_content += 1
        elif content_len < 100:
            short_content += 1
    
    print("=== CONTENT ANALYSIS ===\n")
    print(f"Empty content posts: {empty_content}")
    print(f"Short content posts (< 100 chars): {short_content}")
    print(f"Average content length: {sum(content_lengths) / len(content_lengths):.0f} characters")
    print(f"Min content length: {min(content_lengths)}")
    print(f"Max content length: {max(content_lengths)}")
    print()

def main():
    posts = load_posts('../json/wp_posts.json')
    print(f"Loaded {len(posts)} posts\n")
    
    titles, slugs, content_hashes = analyze_duplicates(posts)
    print_duplicate_report(titles, slugs, content_hashes)
    
    analyze_content_patterns(posts)

if __name__ == "__main__":
    main()