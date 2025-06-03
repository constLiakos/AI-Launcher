"""Markdown rendering utilities."""
import logging

import markdown
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
import re

class ThinkPreprocessor(Preprocessor):
    def run(self, lines):
        text = '\n'.join(lines)
        text = re.sub(r'<think>', r'<div style="font-style: italic; color: rgba(128, 128, 128, 0.7);">', text)
        text = re.sub(r'</think>', r'</div>', text)
        return text.split('\n')

class ThinkExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(ThinkPreprocessor(md), 'think', 175)

class MarkdownRenderer:
    """Handle markdown to HTML conversion."""
    
    def __init__(self, logger:logging):
        self.logger = logger.getChild('markdown_render')
    
    def to_html(self, text):
        """Convert markdown text to HTML."""
        md = markdown.Markdown(extensions=[ThinkExtension()])
        html = md.convert(text)
        return html
