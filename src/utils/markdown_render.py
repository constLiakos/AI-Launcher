"""Markdown rendering utilities."""
import logging
import markdown
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
import re

from managers.style_manager import StyleManager

class ThinkPreprocessor(Preprocessor):
    def __init__(self, md, style_manager:StyleManager):
        super().__init__(md)
        self.style_manager = style_manager

    def run(self, lines):
        text = '\n'.join(lines)

        def replace_think_tags(match):
            content = match.group(1).strip()
            # Only render div if there's actual content
            if content:
                # Added markdown="1" to enable Markdown parsing within the div
                return f'<div markdown="1" style="{self.style_manager.get_llm_thinking_style()}">{content}</div>'
            else:
                return ''  # Remove empty think tags entirely

        # Replace complete <think>content</think> pairs first
        text = re.sub(r'<think>(.*?)</think>', replace_think_tags, text, flags=re.DOTALL)

        def replace_unclosed_think(match):
            content = match.group(1).strip()
            # Apply the same styling as complete tags
            if content:
                # Added markdown="1" to enable Markdown parsing within the div
                return f'<div markdown="1" style="{self.style_manager.get_llm_thinking_style()}">{content}</div>'
            else:
                return ''

        # Look for <think> followed by content that doesn't end with </think>
        # This pattern matches <think> and captures everything after it until end of string
        # but only if there's no </think> in the remaining text
        text = re.sub(r'<think>(?!.*</think>)(.*)', replace_unclosed_think, text, flags=re.DOTALL)

        # Remove any orphaned closing tags (in case there are any left)
        text = re.sub(r'^\s*</think>', '', text, flags=re.MULTILINE)

        return text.split('\n')

class ThinkExtension(Extension):
    def __init__(self, style_manager):
        super().__init__()
        self.style_manager = style_manager

    def extendMarkdown(self, md):
        # The priority of 25 is generally fine. Table processing happens later
        # as a BlockProcessor.
        md.preprocessors.register(ThinkPreprocessor(md, self.style_manager), 'think', 25)

class MarkdownRenderer:
    """Handle markdown to HTML conversion."""

    def __init__(self, style_manager: StyleManager):
        self.logger = logging.getLogger(__name__)
        self.style_manager = style_manager

    def to_html(self, text):
        """Convert markdown text to HTML."""
        # Include 'tables' extension to enable table support
        # and your ThinkExtension.
        md = markdown.Markdown(extensions=[ThinkExtension(self.style_manager), 'sane_lists',  'tables', 'codehilite', 'fenced_code', 'attr_list', 'def_list', 'abbr', 'md_in_html', 'toc', 'nl2br'])
        html = md.convert(text)
        return html
