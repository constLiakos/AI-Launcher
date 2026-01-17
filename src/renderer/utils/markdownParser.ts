import { marked, Tokens } from 'marked';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js';
import katex from 'katex';

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

// Configure LaTeX extension for Marked
const latexExtension = {
  name: 'latex',
  level: 'inline',
  start(src: string) {
    return src.match(/\$/)?.index;
  },
  tokenizer(src: string) {
    // Block Math $$...$$
    const blockRule = /^\$\$([\s\S]*?)\$\$/;
    const blockMatch = blockRule.exec(src);
    if (blockMatch) {
      return {
        type: 'latex',
        raw: blockMatch[0],
        text: blockMatch[1].trim(),
        displayMode: true
      };
    }

    // Inline Math $...$
    const inlineRule = /^\$([^$\n]+?)\$/;
    const inlineMatch = inlineRule.exec(src);
    if (inlineMatch) {
      return {
        type: 'latex',
        raw: inlineMatch[0],
        text: inlineMatch[1].trim(),
        displayMode: false
      };
    }
  },
  renderer(token: any) {
    try {
      return katex.renderToString(token.text, {
        displayMode: token.displayMode,
        throwOnError: false,
        output: 'html'
      });
    } catch (err) {
      console.error('KaTeX error:', err);
      return token.text;
    }
  }
};

marked.use({ extensions: [latexExtension] });
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
 * Parses a Markdown string and returns safe, highlighted HTML with LaTeX support.
 * @param markdownText The raw Markdown text from the AI response.
 * @returns A string containing safe HTML to be rendered.
 */
export function parseMarkdown(markdownText: string, show_think?: boolean): string {
  let processedText = replaceThinkBlocks(markdownText, show_think);

  const dirtyHtml = marked.parse(processedText) as string;
  
  // Αllow specific tags/attributes that KaTeX uses
  const safeHtml = DOMPurify.sanitize(dirtyHtml, {
    ADD_TAGS: ['math', 'semantics', 'mrow', 'mi', 'mo', 'mn', 'msup', 'msub', 'mfrac', 'table', 'tr', 'td', 'th', 'tbody', 'thead'],
    ADD_ATTR: ['xmlns', 'display', 'class', 'style', 'aria-hidden']
  });
  
  return safeHtml;
}