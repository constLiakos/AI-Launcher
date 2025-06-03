"""Markdown rendering utilities."""
import logging

import markdown
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
import re

class ThinkPreprocessor(Preprocessor):
    def run(self, lines):
        text = '\n'.join(lines)
        
        def replace_think_tags(match):
            content = match.group(1).strip()
            # Only render div if there's actual content
            if content:
                return f'<div style="font-style: italic; color: rgba(128, 128, 128, 0.7);">{content}</div>'
            else:
                return ''  # Remove empty think tags entirely
        
        text = re.sub(r'<think>(.*?)</think>', replace_think_tags, text, flags=re.DOTALL)
        
        def replace_unclosed_think(match):
            content = match.group(1).strip()
            # Apply the same styling as complete tags
            if content:
                return f'<div style="font-style: italic; color: rgba(128, 128, 128, 0.7);">{content}</div>'
            else:
                return ''

        text = re.sub(r'<think>(?!.*</think>)(.*)', replace_unclosed_think, text, flags=re.DOTALL)
        text = re.sub(r'^\s*</think>', '', text, flags=re.MULTILINE)
        
        return text.split('\n')

class ThinkExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(ThinkPreprocessor(md), 'think', 175)

class MarkdownRenderer:
    """Handle markdown to HTML conversion."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger.getChild('markdown_render')
    
    def to_html(self, text):
        """Convert markdown text to HTML."""
        md = markdown.Markdown(extensions=[ThinkExtension()])
        html = md.convert(text)
        return html