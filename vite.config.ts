import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';
import { resolve } from 'path';

export default defineConfig({
  root: resolve(__dirname, 'src/renderer'), 
  base: './', 
  build: {
    outDir: resolve(__dirname, 'dist/renderer'), 
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/renderer/index.html'),
        settings: resolve(__dirname, 'src/renderer/settings.html')
      }
    },
    assetsDir: 'assets' 
  },
  server: {
    port: 5173,
  },
  css: {
    devSourcemap: true
  },
  define: {

    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV),
    '__IS_DEV__': JSON.stringify(process.env.NODE_ENV === 'development'),
  },

  resolve: {
    dedupe: ['react', 'react-dom'], 
    alias: {

    }
  },
  plugins: [tsconfigPaths()]
});