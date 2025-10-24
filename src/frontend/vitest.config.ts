import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  test: {
    setupFiles: './vitest/setupTests.ts',
    globals: true,
    environment: 'jsdom',
  },
  resolve: {
    alias: {
      '@api': resolve(__dirname, 'src/api'),
      '@components': resolve(__dirname, 'src/components'),
      '@core': resolve(__dirname, 'src/components/core'),
      '@containers': resolve(__dirname, 'src/containers'),
      '@shared': resolve(__dirname, 'src/shared'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@generated': resolve(__dirname, 'src/__generated__'),
      '@restgenerated': resolve(__dirname, 'src/restgenerated'),
      src: resolve(__dirname, 'src'),
    },
  },
});
