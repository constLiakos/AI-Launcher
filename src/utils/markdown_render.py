"""Markdown rendering utilities."""
import logging
import re
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


class MarkdownRenderer:
    """Handle markdown to HTML conversion."""
    
    def __init__(self, logger:logging):
        self.logger = logger.getChild('markdown_render')
        self.extensions = ['codehilite', 'fenced_code', 'tables'] if MARKDOWN_AVAILABLE else []
    
    def to_html(self, text):
        """Convert markdown text to HTML."""
        if not text:
            return ""
            
        if MARKDOWN_AVAILABLE:
            try:
                return markdown.markdown(text, extensions=self.extensions)
            except Exception as e:
                print(f"Markdown conversion failed: {e}")
                return self._basic_markdown_to_html(text)
        else:
            return self._basic_markdown_to_html(text)
    
    def _basic_markdown_to_html(self, text):
        """Basic markdown to HTML conversion without external dependencies."""
        # Escape HTML
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Code blocks
        text = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code>\2</code></pre>', text, flags=re.DOTALL)
        
        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Headers
        text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)

        # Horizontal rules
        text = re.sub(r'^---+$', r'<hr>', text, flags=re.MULTILINE)
        
        # Convert line breaks to paragraphs
        paragraphs = text.split('\n\n')
        html_paragraphs = []
        for p in paragraphs:
            if p.strip() and not p.strip().startswith('<'):
                html_paragraphs.append(f'<p>{p.replace(chr(10), "<br>")}</p>')
            else:
                html_paragraphs.append(p)
        
        return ''.join(html_paragraphs)