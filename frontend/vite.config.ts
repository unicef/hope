import { defineConfig, splitVendorChunkPlugin } from 'vite';
import polyfillNode from 'rollup-plugin-polyfill-node';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig({
  assetsInclude: ['**/*.png'],
  base: '',
  plugins: [tsconfigPaths(), react(), splitVendorChunkPlugin(), polyfillNode()],
  resolve: {
    mainFields: [],
  },
  esbuild: {
    loader: 'tsx',
    include: /\.[jt]sx?$/,
    exclude: /node_modules/,
    jsxFactory: 'React.createElement',
    jsxFragment: 'React.Fragment',
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
