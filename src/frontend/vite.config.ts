import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import csp from 'vite-plugin-csp-guard';
import { existsSync, mkdirSync, writeFileSync } from 'fs';
import { dirname } from 'path';

let cspReportUri = null;
const sentryDsn = process.env.SENTRY_DSN;

if (process.env.NODE_ENV !== 'development' && sentryDsn) {
  const sentryKey = sentryDsn.split('@')[0].split('//')[1];
  const sentryId = sentryDsn.split('@')[1].split('/')[1];
  cspReportUri = `https://excubo.unicef.io/api/${sentryId}/security/?sentry_key=${sentryKey}`;
}
function generateNginxHeaderFile(builtPolicy: string) {
  let header = `add_header Content-Security-Policy-Report-Only "${builtPolicy};`;
  // `add_header Content-Security-Policy "${builtPolicy};`; // Uncomment this to enforce CSP
  if (cspReportUri) {
    header += ` report-uri ${cspReportUri}; report-to ${cspReportUri};`;
  }
  header += '";';

  const filePath = 'dist/nginx-csp-header.conf';
  const dir = dirname(filePath);

  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }

  writeFileSync(filePath, header);
}

export default defineConfig({
  assetsInclude: ['**/*.png'],
  base: '',
  plugins: [
    tsconfigPaths(),
    react(),
    csp({
      dev: {
        run: true,
      },
      algorithm: 'sha256',
      policy: {
        'default-src': ["'self'"],
        'frame-ancestors': ["'none'"],
        'style-src': [
          "'self'",
          "'unsafe-inline'",
          "'unsafe-eval'",
          'https://fonts.googleapis.com',
        ],
        'style-src-elem': [
          "'self'",
          "'unsafe-inline'",
          "'unsafe-eval'",
          'https://fonts.googleapis.com',
        ],
        'font-src': ["'self'", 'data:', 'https://fonts.gstatic.com'],
        'img-src': ["'self'", 'data:'],
        'connect-src': [
          "'self'",
          'https://excubo.unicef.io',
          'https://sentry.io',
        ],
      },
      build: {
        sri: true,
      },
    }),

    {
      name: 'vite-plugin-generate-nginx-csp',
      apply: 'build',
      closeBundle() {
        const builtPolicy =
          "default-src 'self'; frame-ancestors 'none'; style-src 'self' 'unsafe-inline' 'unsafe-eval' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self' https://excubo.unicef.io https://sentry.io" +
          (cspReportUri
            ? `; report-uri ${cspReportUri}; report-to ${cspReportUri}`
            : '');

        generateNginxHeaderFile(builtPolicy);
      },
    },
  ],
  resolve: {
    mainFields: [],
  },
  optimizeDeps: {
    esbuildOptions: {
      loader: {
        '.ts': 'ts',
        '.tsx': 'tsx',
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
