#!/usr/bin/env python3
"""
Deduplicate WordPress posts - reads from json folder, never modifies source
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path

def load_posts(json_path):
    """Load posts from JSON file"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_content_hash(post):
    """Create hash of post content for duplicate detection"""
    content = post.get('content', {}).get('rendered', '')
    title = post.get('title', {}).get('rendered', '')
    combined = f"{title}\n{content}".strip()
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def find_duplicates(posts):
    """Find duplicate posts by content hash and title"""
    seen_hashes = {}
    seen_titles = {}
    duplicates = []
    unique_posts = []
    
    for post in posts:
        content_hash = create_content_hash(post)
        title = post.get('title', {}).get('rendered', '').strip().lower()
        post_id = post.get('id')
        post_date = post.get('date', '')
        
        # Check for content duplicates
        if content_hash in seen_hashes:
            original_post = seen_hashes[content_hash]
            duplicates.append({
                'type': 'content_duplicate',
                'original_id': original_post['id'],
                'original_date': original_post['date'],
                'duplicate_id': post_id,
                'duplicate_date': post_date,
                'title': title
            })
            continue
        
        # Check for title duplicates
        if title and title in seen_titles:
            original_post = seen_titles[title]
            # Keep the newer post for title duplicates
            if post_date > original_post['date']:
                # Remove the older post from unique_posts
                unique_posts = [p for p in unique_posts if p['id'] != original_post['id']]
                duplicates.append({
                    'type': 'title_duplicate',
                    'original_id': original_post['id'],
                    'original_date': original_post['date'],
                    'duplicate_id': post_id,
                    'duplicate_date': post_date,
                    'title': title,
                    'action': 'kept_newer'
                })
                seen_titles[title] = post
                seen_hashes[content_hash] = post
                unique_posts.append(post)
            else:
                duplicates.append({
                    'type': 'title_duplicate',
                    'original_id': original_post['id'],
                    'original_date': original_post['date'],
                    'duplicate_id': post_id,
                    'duplicate_date': post_date,
                    'title': title,
                    'action': 'kept_older'
                })
        else:
            # Unique post
            seen_hashes[content_hash] = post
            if title:
                seen_titles[title] = post
            unique_posts.append(post)
    
    return unique_posts, duplicates

def save_deduplication_report(duplicates, output_path):
    """Save duplicate report to file"""
    report_path = Path(output_path) / 'deduplication_report.json'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_duplicates': len(duplicates),
            'duplicates': duplicates
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Deduplication report saved to: {report_path}")

def save_clean_posts(posts, output_path):
    """Save deduplicated posts to clean JSON file"""
    clean_path = Path(output_path) / 'clean_posts.json'
    
    with open(clean_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    
    print(f"Clean posts saved to: {clean_path}")

def main():
    json_path = Path('../json/wp_posts.json')
    output_path = Path('../output')
    
    # Ensure output directory exists
    output_path.mkdir(exist_ok=True)
    
    print("Loading posts...")
    posts = load_posts(json_path)
    print(f"Loaded {len(posts)} posts")
    
    print("Finding duplicates...")
    unique_posts, duplicates = find_duplicates(posts)
    
    print(f"Found {len(duplicates)} duplicates")
    print(f"Keeping {len(unique_posts)} unique posts")
    
    # Save results
    save_deduplication_report(duplicates, output_path)
    save_clean_posts(unique_posts, output_path)
    
    print("\nDeduplication complete!")

if __name__ == "__main__":
    main()