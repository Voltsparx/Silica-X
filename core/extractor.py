# core/extractor.py

import re

def extract_bio(html):
    """
    Extract a short bio/description from HTML meta tags.
    """
    patterns = [
        r'<meta name="description" content="(.*?)"',
        r'<meta property="og:description" content="(.*?)"'
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.I | re.S)
        if match:
            return match.group(1).strip()

    return None


def extract_links(html):
    """
    Extract all unique external HTTP/HTTPS links from HTML.
    """
    return list(set(re.findall(r'href="(https?://[^"]+)"', html)))
