# WordPress Blog Content Cleaner

This project contains scripts to clean up and deduplicate blog content imported from WordPress.

## Overview

The cleaner package processes blog posts from two sources:
1. **WordPress JSON export** (`json/wp_posts.json`) - converted to markdown with `type: "wp"`
2. **Existing markdown posts** (`posts/` directory) - processed with `type: "rain"`

## Directory Structure

```
├── json/               # Source WordPress JSON data (READ-ONLY)
│   └── wp_posts.json
├── posts/              # Source markdown posts (READ-ONLY) 
│   └── *.md files
├── cleaner/            # Python processing scripts
│   ├── main.py         # Main entry point
│   ├── deduplicate.py  # Remove WordPress duplicates
│   ├── process_posts.py # Convert WordPress to markdown
│   ├── compare_posts.py # Find non-WordPress posts
│   └── process_rain_posts.py # Process rain posts
└── output/             # Generated markdown files (WRITE)
    └── *.md files with front matter
```

## Usage

### Run Complete Pipeline
```bash
cd cleaner
python3 main.py
```

### Run Individual Steps
```bash
# Step 1: Deduplicate WordPress posts
python3 deduplicate.py

# Step 2: Convert WordPress to markdown
python3 process_posts.py

# Step 3: Find rain posts
python3 compare_posts.py

# Step 4: Process rain posts
python3 process_rain_posts.py
```

## Additional Cleaning

Key Issues to Fix in Import Tool:

  1. YAML String Escaping

  # Fix this:
  title: "The \"Goal\" of Performance Tuning"

  # To this:
  title: "The \"Goal\" of Performance Tuning"
  # OR better yet:
  title: 'The "Goal" of Performance Tuning'  # Use single quotes to avoid escaping

  2. HTML in YAML Values

  # Fix this:
  subtitle: "<img class=\"cover\" src=https://example.com>"

  # To this:
  subtitle: "<img class='cover' src='https://example.com'>"
  # OR escape properly:
  subtitle: "<img class=\"cover\" src=\"https://example.com\">"

  3. Empty/Malformed HTML

  # Fix this:
  subtitle: "<img class=\"cover\" src=>"

  # To this (remove if empty):
  subtitle: ""
  # OR provide proper fallback

  4. Filename Sanitization

  # Consider converting:
  The-__Goal__-of-Performance.md
  # To:
  The-Goal-of-Performance.md

  Import Tool Recommendations:

  1. Add YAML validation before writing files
  2. Use proper escaping functions for YAML strings
  3. Sanitize HTML attributes (single quotes or proper escaping)
  4. Validate image URLs before including them
  5. Add filename sanitization to remove problematic characters

## Output

All markdown files are generated in `output/` with front matter:

### WordPress Posts (`type: "wp"`)
```yaml
---
title: "Post Title"
subtitle: "Subtitle from content"
category: "category"
tags: []
date: "2024-01-01"
type: "wp"
wordpress_id: 123
---
```

### Rain Posts (`type: "rain"`)
```yaml
---
title: "Post Title"
subtitle: "Subtitle from content" 
category: "uncategorized"
tags: []
date: "2024-01-01"
type: "rain"
---
```

## Features

- **Non-destructive**: Never modifies source data in `json/` or `posts/`
- **Idempotent**: Can be re-run safely to get identical results
- **Deduplication**: Removes duplicate posts based on content and title
- **HTML conversion**: Converts WordPress HTML to clean markdown
- **Entity decoding**: Properly handles HTML entities (&amp;, &quot;, etc.)
- **Smart comparison**: Handles filename variations (hyphens vs underscores)

## File Naming

Output files use the format: `YYYY-MM-DD-title.md`

## Processing Stats

Last run processed:
- 2,810 WordPress posts (77 duplicates removed)
- 2,804 rain posts (673 duplicates avoided)
- Total: 5,614 unique blog posts

## Safety

All scripts are designed to be safe:
- Source directories (`json/`, `posts/`) are never modified
- Only read operations on source data
- All output goes to dedicated `output/` directory
- Can be run multiple times without side effects