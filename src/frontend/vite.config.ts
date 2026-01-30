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
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (
              id.includes('@mui/') ||
              id.includes('@emotion/') ||
              id.includes('styled-components') ||
              id.includes('@base-ui-components')
            )
              return 'vendor-mui';

            if (
              id.includes('chart.js') ||
              id.includes('chartjs-plugin') ||
              id.includes('react-chartjs')
            )
              return 'vendor-charts';

            if (id.includes('/formik/') || id.includes('/yup/'))
              return 'vendor-forms';

            if (
              id.includes('/moment/') ||
              id.includes('/date-fns/') ||
              id.includes('@date-io/')
            )
              return 'vendor-dates';

            if (id.includes('@sentry/')) return 'vendor-sentry';

            if (
              id.includes('/react-dom/') ||
              id.includes('/react-router') ||
              id.includes('/react/') ||
              id.includes('/@tanstack/') ||
              id.includes('/react-i18next/') ||
              id.includes('/i18next/')
            )
              return 'vendor-react';

            return 'vendor-misc';
          }

          // Feature chunks
          if (
            id.includes('/components/grievances/') ||
            id.includes('/pages/grievances/') ||
            id.includes('/routers/GrievanceRoutes')
          )
            return 'feature-grievances';

          if (
            id.includes('/components/paymentmodule') ||
            id.includes('/pages/paymentmodule') ||
            id.includes('/tables/paymentmodule') ||
            id.includes('/routers/PaymentModuleRoutes') ||
            id.includes('/routers/PaymentVerificationRoutes') ||
            id.includes('/components/payments/') ||
            id.includes('/pages/payments/') ||
            id.includes('/tables/payments/')
          )
            return 'feature-payments';

          if (
            id.includes('/components/accountability/') ||
            id.includes('/pages/accountability/') ||
            id.includes('/tables/Communication/') ||
            id.includes('/tables/Surveys/') ||
            id.includes('/tables/Feedback/') ||
            id.includes('/routers/AccountabilityRoutes')
          )
            return 'feature-accountability';

          if (
            id.includes('/components/targeting/') ||
            id.includes('/pages/targeting/') ||
            id.includes('/tables/targeting/') ||
            id.includes('/routers/TargetingRoutes') ||
            id.includes('/forms/TargetingCriteria') ||
            id.includes('/dialogs/targetPopulation/')
          )
            return 'feature-targeting';

          if (
            id.includes('/components/rdi/') ||
            id.includes('/pages/rdi/') ||
            id.includes('/tables/rdi/') ||
            id.includes('/routers/RegistrationRoutes')
          )
            return 'feature-rdi';

          if (
            id.includes('/components/population/') ||
            id.includes('/pages/population/') ||
            id.includes('/tables/population/') ||
            id.includes('/components/people/') ||
            id.includes('/pages/people/') ||
            id.includes('/tables/people/') ||
            id.includes('/routers/PopulationRoutes') ||
            id.includes('/components/periodicDataUpdates/')
          )
            return 'feature-population';

          if (
            id.includes('/components/programs/') ||
            id.includes('/pages/program/') ||
            id.includes('/tables/ProgrammesTable/') ||
            id.includes('/tables/ProgramCycle') ||
            id.includes('/routers/ProgramRoutes') ||
            id.includes('/dialogs/programs/')
          )
            return 'feature-programs';
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
