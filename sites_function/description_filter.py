from django import template
import re

register = template.Library()

@register.filter
def strip_html(value):
    """Remove HTML tags from text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', value)

@register.filter
def truncate_words(value, word_count=30):
    """Truncate text to a specified word count."""
    words = value.split()
    if len(words) > word_count:
        return ' '.join(words[:word_count]) + '...'
    return value
