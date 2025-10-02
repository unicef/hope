import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig({
  assetsInclude: ['**/*.png'],
  base: '',
  plugins: [tsconfigPaths(), react()],
  resolve: {
    mainFields: [],
  },
  esbuild: {
    loader: 'tsx',
    include: /\.[jt]sx?$/,
    exclude: /node_modules/,
    jsxFactory: 'createElement',
    jsxFragment: 'Fragment',
  },
  build: {
    outDir: 'build',
    manifest: true,
    rollupOptions: {
      input: '/src/main.tsx',
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        },
      },
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
