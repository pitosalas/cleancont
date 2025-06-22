#!/usr/bin/env python3
"""
Utilities for safe YAML generation and validation
"""
import re
from html import unescape

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
from pathlib import Path


def sanitize_yaml_string(text):
    """
    Safely prepare a string for YAML output by:
    1. Unescaping HTML entities
    2. Choosing appropriate quoting strategy
    3. Properly escaping when needed
    """
    if not text:
        return ""
    
    # Unescape HTML entities
    text = unescape(text)
    
    # Remove any leading/trailing whitespace
    text = text.strip()
    
    # If string contains double quotes but no single quotes, use single quotes
    if '"' in text and "'" not in text:
        return f"'{text}'"
    
    # If string contains single quotes but no double quotes, use double quotes
    if "'" in text and '"' not in text:
        return f'"{text}"'
    
    # If string contains both or neither, use double quotes with escaping
    escaped_text = text.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped_text}"'


def sanitize_html_in_yaml(text):
    """
    Clean up HTML content that will be used in YAML values
    """
    if not text:
        return ""
    
    # Fix malformed HTML attributes - replace empty src attributes
    text = re.sub(r'src\s*=\s*>', 'src="">', text)
    text = re.sub(r'src\s*=\s*$', 'src=""', text)
    
    # Convert double quotes in HTML attributes to single quotes
    # This regex matches HTML attributes with double quotes
    def fix_html_quotes(match):
        tag = match.group(0)
        # Replace double quotes around attribute values with single quotes
        tag = re.sub(r'="([^"]*)"', r"='\1'", tag)
        return tag
    
    # Apply to HTML tags
    text = re.sub(r'<[^>]+>', fix_html_quotes, text)
    
    return text


def sanitize_markdown_links_in_yaml(text):
    """
    Clean up markdown links that can cause YAML parsing issues
    """
    if not text:
        return ""
    
    # Handle various markdown link patterns that can break YAML
    
    # Pattern 1: Complete markdown links [text](url)
    def clean_complete_link(match):
        link_text = match.group(1)
        return link_text
    
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', clean_complete_link, text)
    
    # Pattern 2: Incomplete markdown links [text](partial_url...
    # This handles cases where URLs are truncated
    def clean_incomplete_link(match):
        link_text = match.group(1)
        return link_text
    
    text = re.sub(r'\[([^\]]+)\]\([^)]*\.{3,}', clean_incomplete_link, text)
    text = re.sub(r'\[([^\]]+)\]\([^)]*$', clean_incomplete_link, text)
    
    # Pattern 3: Just remove any remaining brackets and parentheses that could cause issues
    text = re.sub(r'\[([^\]]+)\]\([^)]*', r'\1', text)
    
    # Remove any remaining problematic characters that might break YAML
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def sanitize_filename(filename):
    """
    Sanitize filename by removing problematic characters
    """
    if not filename:
        return "untitled.md"
    
    # Remove file extension for processing
    name_part = filename.replace('.md', '')
    
    # Replace multiple consecutive underscores or hyphens with single hyphen
    name_part = re.sub(r'[-_]{2,}', '-', name_part)
    
    # Remove any remaining problematic characters
    name_part = re.sub(r'[^\w\-.]', '-', name_part)
    
    # Remove leading/trailing hyphens
    name_part = name_part.strip('-')
    
    # Ensure we have something
    if not name_part:
        name_part = "untitled"
    
    return f"{name_part}.md"


def validate_yaml_front_matter(front_matter_text):
    """
    Validate that the front matter is valid YAML
    Returns (is_valid, error_message)
    """
    if not HAS_YAML:
        # Basic validation without PyYAML - just check for obvious syntax issues
        try:
            if front_matter_text.startswith('---'):
                parts = front_matter_text.split('---', 2)
                if len(parts) >= 2:
                    yaml_content = parts[1].strip()
                else:
                    return False, "Invalid front matter format"
            else:
                yaml_content = front_matter_text
            
            # Basic checks for common YAML issues
            lines = yaml_content.split('\n')
            for line in lines:
                line = line.strip()
                if line and ':' in line:
                    # Check for unbalanced quotes
                    if line.count('"') % 2 != 0:
                        return False, f"Unbalanced quotes in line: {line}"
                    if line.count("'") % 2 != 0:
                        return False, f"Unbalanced single quotes in line: {line}"
            
            return True, ""
        except Exception as e:
            return False, f"Basic validation error: {str(e)}"
    
    try:
        # Extract just the YAML content between the --- markers
        if front_matter_text.startswith('---'):
            parts = front_matter_text.split('---', 2)
            if len(parts) >= 2:
                yaml_content = parts[1].strip()
            else:
                return False, "Invalid front matter format"
        else:
            yaml_content = front_matter_text
        
        # Try to parse the YAML
        yaml.safe_load(yaml_content)
        return True, ""
    
    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def create_safe_front_matter(title, subtitle, category, tags, date, post_type, wordpress_id=None):
    """
    Create safe front matter with proper escaping and validation
    """
    # Sanitize all string inputs
    safe_title = sanitize_yaml_string(title)
    # Apply both HTML and markdown link sanitization to subtitle
    subtitle_cleaned = sanitize_markdown_links_in_yaml(sanitize_html_in_yaml(subtitle))
    safe_subtitle = sanitize_yaml_string(subtitle_cleaned)
    safe_category = sanitize_yaml_string(category)
    
    # Handle tags - ensure it's a proper list format
    if isinstance(tags, list):
        if tags:
            # Sanitize each tag
            safe_tags = [sanitize_yaml_string(str(tag)) for tag in tags]
            tags_yaml = "[" + ", ".join(safe_tags) + "]"
        else:
            tags_yaml = "[]"
    else:
        tags_yaml = "[]"
    
    # Build front matter
    front_matter_lines = [
        "---",
        f"title: {safe_title}",
        f"subtitle: {safe_subtitle}",
        f"category: {safe_category}",
        f"tags: {tags_yaml}",
        f"date: {sanitize_yaml_string(date)}",
        f"type: {sanitize_yaml_string(post_type)}"
    ]
    
    # Add WordPress ID if provided
    if wordpress_id is not None:
        front_matter_lines.append(f"wordpress_id: {wordpress_id}")
    
    front_matter_lines.extend(["---", ""])
    
    front_matter_text = "\n".join(front_matter_lines)
    
    # Validate the generated YAML
    is_valid, error_msg = validate_yaml_front_matter(front_matter_text)
    if not is_valid:
        print(f"Warning: Generated invalid YAML front matter: {error_msg}")
        print(f"Title: {title}")
        print(f"Subtitle: {subtitle}")
        # Return a basic fallback
        return f"""---
title: "Post Title"
subtitle: ""
category: "uncategorized"
tags: []
date: "{date}"
type: "{post_type}"
---

"""
    
    return front_matter_text