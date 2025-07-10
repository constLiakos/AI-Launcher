import { marked, Tokens } from 'marked';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js';

const markedExtension = {
  async: false,
  renderer: {
    code(token: Tokens.Code): string {
      const language = token.lang || 'plaintext';
      const validLanguage = hljs.getLanguage(language) ? language : 'plaintext';
      const highlightedCode = hljs.highlight(token.text, { language: validLanguage }).value;
      
      return `<pre><code class="hljs language-${validLanguage}">${highlightedCode}</code></pre>`;
    }
  },
  
  gfm: true,
  breaks: true,
};

marked.use(markedExtension);

/**
 * Helper to replace <think>...</think> or <think>... (unclosed) with the desired structure.
 */
function replaceThinkBlocks(text: string, show_think?: boolean): string {
  return text.replace(
    /<think>([\s\S]*?)(<\/think>|$)/g,
    (_, content) => `
<div class="think-container" ${show_think ? '' : 'collapsed'}>
  <div class="think-header">
    <button class="think-toggle-btn" aria-label="Toggle thinking process" aria-expanded="false">
      <svg class="icon-expand" viewBox="0 0 24 24"><path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6z"/></svg>
      <svg class="icon-collapse" viewBox="0 0 24 24"><path d="M7.41 15.41L12 10.83l4.59 4.58L18 14l-6-6-6 6z"/></svg>
    </button>
    <span class="think-collapsed-label">Thinking...</span>
  </div>
  <div class="think-content">
    ${content.trim()}
  </div>
</div>
`
  );
}

/**
 * Parses a Markdown string and returns safe, highlighted HTML.
 * @param markdownText The raw Markdown text from the AI response.
 * @returns A string containing safe HTML to be rendered.
 */
export function parseMarkdown(markdownText: string, show_think?:boolean): string {
  let processedText = replaceThinkBlocks(markdownText, show_think);

  const dirtyHtml = marked.parse(processedText) as string;
  const safeHtml = DOMPurify.sanitize(dirtyHtml);
  
  return safeHtml;
}