import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';

// https://vitejs.dev/config/
export default defineConfig({
  assetsInclude: ['**/*.png'],
  plugins: [tsconfigPaths(), react()],
  esbuild: {
    loader: 'tsx',
    include: /\.[jt]sx?$/,
    exclude: /node_modules/,
    jsxFactory: 'React.createElement',
    jsxFragment: 'React.Fragment',
  },
  build: {
    outDir: 'build',
  },
  server: {
    port: 3000,
    host: true,
  },
});
