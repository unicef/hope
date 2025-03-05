import { defineConfig, splitVendorChunkPlugin } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig({
  assetsInclude: ['**/*.png'],
  base: '',
  plugins: [tsconfigPaths(), react(), splitVendorChunkPlugin()],
  resolve: {
    mainFields: [],
  },
  optimizeDeps: {
    esbuildOptions: {
      loader: {
        '.ts': 'ts', // Pure TypeScript for .ts
        '.tsx': 'tsx', // TypeScript with JSX for .tsx
      },
    },
  },
  build: {
    outDir: 'build',
    manifest: true,
    rollupOptions: {
      input: '/src/main.tsx',
    },
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
      },
    },
  },
});
