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
        self.extensions = ['codehilite', 'fenced_code', 'tables', 'toc'] if MARKDOWN_AVAILABLE else []
    
    def to_html(self, text):
        """Convert markdown text to HTML."""
        if not text:
            return ""
            
        if MARKDOWN_AVAILABLE:
            try:
                return markdown.markdown(text, extensions=self.extensions)
            except Exception as e:
                self.logger.error(f"Markdown conversion failed: {e}")
                return self._basic_markdown_to_html(text)
        else:
            return self._basic_markdown_to_html(text)
    
    def _basic_markdown_to_html(self, text):
        """Basic markdown to HTML conversion without external dependencies."""
        # Escape HTML
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Convert HTTP links
        text = re.sub(r'\b(http[s]?://[^\s]+)', r'<a href="\1">\1</a>', text)
        
        # Code blocks with language support
        text = re.sub(r'```(\w+)?\n(.*?)\n```', 
                     lambda m: f'<pre><code class="language-{m.group(1) or "text"}">{m.group(2)}</code></pre>', 
                     text, flags=re.DOTALL)
        
        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # Links [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Images ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', r'<img src="\2" alt="\1">', text)
        
        # Bold and italic (handle nested)
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Strikethrough
        text = re.sub(r'~~(.*?)~~', r'<del>\1</del>', text)
        
        # Headers (up to h6)
        text = re.sub(r'^###### (.*?)$', r'<h6>\1</h6>', text, flags=re.MULTILINE)
        text = re.sub(r'^##### (.*?)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
        text = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # Blockquotes
        text = re.sub(r'^> (.*)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
        
        # Unordered lists
        text = re.sub(r'^[*+-] (.*)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        text = re.sub(r'(<li>.*</li>\n?)+', r'<ul>\g<0></ul>', text)
        
        # Ordered lists
        text = re.sub(r'^\d+\. (.*)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        text = re.sub(r'(<li>.*</li>\n?)+', lambda m: f'<ol>{m.group(0)}</ol>' if '.' in text[:m.start()] else m.group(0), text)
        
        # Horizontal rules
        text = re.sub(r'^---+$', r'<hr>', text, flags=re.MULTILINE)
        text = re.sub(r'^\*\*\*+$', r'<hr>', text, flags=re.MULTILINE)
        
        # Tables (basic support)
        def process_table(match):
            lines = [line.strip() for line in match.group(0).strip().split('\n') if line.strip()]
            if len(lines) < 2:
                return match.group(0)
            
            header = lines[0]
            separator = lines[1]
            rows = lines[2:] if len(lines) > 2 else []
            
            # Check if separator line contains dashes and pipes
            if not re.search(r'[\-\|]', separator) or '|' not in separator:
                return match.group(0)
            
            html = '<table>\n'
            
            # Header
            html += '<thead><tr>'
            header_cells = [cell.strip() for cell in header.split('|')]
            # Remove empty cells from start/end if they exist
            if header_cells and not header_cells[0]:
                header_cells = header_cells[1:]
            if header_cells and not header_cells[-1]:
                header_cells = header_cells[:-1]
            
            for cell in header_cells:
                html += f'<th>{cell}</th>'
            html += '</tr></thead>\n'
            
            # Body
            if rows:
                html += '<tbody>'
                for row in rows:
                    html += '<tr>'
                    row_cells = [cell.strip() for cell in row.split('|')]
                    # Remove empty cells from start/end if they exist
                    if row_cells and not row_cells[0]:
                        row_cells = row_cells[1:]
                    if row_cells and not row_cells[-1]:
                        row_cells = row_cells[:-1]
                    
                    for cell in row_cells:
                        html += f'<td>{cell}</td>'
                    html += '</tr>'
                html += '</tbody>'
            
            html += '</table>'
            return html
        
        # Match table patterns
        text = re.sub(r'^\|.*\|[ \t]*\n\|[\s\-:|]*\|[ \t]*\n(?:\|.*\|[ \t]*\n?)*', 
                     process_table, text, flags=re.MULTILINE)
        
        # Convert line breaks to paragraphs
        paragraphs = text.split('\n\n')
        html_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p and not re.match(r'^<(?:h[1-6]|ul|ol|blockquote|table|hr|pre)', p):
                html_paragraphs.append(f'<p>{p.replace(chr(10), "<br>")}</p>')
            else:
                html_paragraphs.append(p)
        
        return '\n'.join(html_paragraphs)