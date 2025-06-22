#!/usr/bin/env python3
"""
Convert HTML content to clean markdown
"""
import re
from html import unescape
from urllib.parse import urljoin, urlparse

def strip_html_tags(html):
    """Remove HTML tags and return plain text"""
    # Remove script and style elements completely
    html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Convert common HTML entities
    html = unescape(html)
    
    # Remove all HTML tags
    html = re.sub(r'<[^>]+>', '', html)
    
    # Clean up whitespace
    html = re.sub(r'\s+', ' ', html)
    html = html.strip()
    
    return html

def html_to_markdown(html):
    """Convert HTML to markdown with basic formatting preserved"""
    if not html or not html.strip():
        return ""
    
    # Unescape HTML entities first
    content = unescape(html)
    
    # Convert headings
    content = re.sub(r'<h([1-6])[^>]*>(.*?)</h\1>', lambda m: '#' * int(m.group(1)) + ' ' + strip_html_tags(m.group(2)), content, flags=re.IGNORECASE | re.DOTALL)
    
    # Convert paragraphs
    content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Convert line breaks
    content = re.sub(r'<br[^>]*/?>', '\n', content, flags=re.IGNORECASE)
    
    # Convert bold
    content = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'**\2**', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Convert italic
    content = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', r'*\2*', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Convert links
    content = re.sub(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Convert images
    content = re.sub(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']*)["\'][^>]*/?>', r'![\2](\1)', content, flags=re.IGNORECASE)
    content = re.sub(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*/?>', r'![](\1)', content, flags=re.IGNORECASE)
    
    # Convert unordered lists
    content = re.sub(r'<ul[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</ul>', '\n', content, flags=re.IGNORECASE)
    content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Convert ordered lists
    content = re.sub(r'<ol[^>]*>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'</ol>', '\n', content, flags=re.IGNORECASE)
    
    # Handle ordered list items (simple numbering)
    ol_counter = 1
    def replace_ol_item(match):
        nonlocal ol_counter
        result = f"{ol_counter}. {match.group(1)}"
        ol_counter += 1
        return result
    
    # Convert blockquotes
    content = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', r'> \1', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Convert code blocks
    content = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', r'```\n\1\n```', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<pre[^>]*>(.*?)</pre>', r'```\n\1\n```', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', content, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove remaining HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Clean up whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Multiple newlines to double
    content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single
    content = content.strip()
    
    return content

def extract_excerpt(content, max_length=200):
    """Extract a clean excerpt from content"""
    if not content:
        return ""
    
    # Remove markdown formatting for excerpt
    excerpt = re.sub(r'[*_`#>\-\[\]()]', '', content)
    excerpt = re.sub(r'\s+', ' ', excerpt).strip()
    
    if len(excerpt) <= max_length:
        return excerpt
    
    # Truncate at word boundary
    truncated = excerpt[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:  # If we can truncate at a reasonable word boundary
        truncated = truncated[:last_space]
    
    return truncated + "..."

def main():
    # Test function
    test_html = """
    <p>This is a <strong>test</strong> paragraph with <em>emphasis</em> and a <a href="https://example.com">link</a>.</p>
    <h2>A Heading</h2>
    <ul>
        <li>First item</li>
        <li>Second item</li>
    </ul>
    <blockquote>This is a quote</blockquote>
    """
    
    result = html_to_markdown(test_html)
    print("Test conversion:")
    print(result)

if __name__ == "__main__":
    main()