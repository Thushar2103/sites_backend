import re

def strip_html(content):
    """Remove HTML tags from a string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', content)

def truncate_words(content, word_count=30):
    """Truncate the string to the given number of words."""
    words = content.split()
    if len(words) > word_count:
        return ' '.join(words[:word_count]) + '...'
    return content
