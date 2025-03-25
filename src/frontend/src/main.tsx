import * as Sentry from '@sentry/react';
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js';
import { createRoot } from 'react-dom/client';
import packageJson from '../package.json';
import { App } from './App';
import setupInternalization from './i18n';
import './index.css';
import './global.css';
import React from 'react';
import {
  createRoutesFromChildren,
  matchRoutes,
  useLocation,
  useNavigationType,
} from 'react-router-dom';
import { FONT } from './theme';

ChartJS.register(
  ArcElement,
  LinearScale,
  CategoryScale,
  BarElement,
  Tooltip,
  Legend,
);
ChartJS.defaults.font.family = FONT;
ChartJS.defaults.plugins.tooltip.padding = 12;
ChartJS.defaults.plugins.tooltip.cornerRadius = 2;
ChartJS.defaults.plugins.tooltip.mode = 'point';
ChartJS.defaults.plugins.legend.position = 'bottom';
ChartJS.defaults.plugins.legend.labels.usePointStyle = true;
ChartJS.defaults.plugins.legend.labels.boxWidth = 8;

setupInternalization();
// eslint-disable-next-line no-undef
if (process.env.NODE_ENV !== 'development' && window.SENTRY_DSN) {
  Sentry.init({
    dsn: window.SENTRY_DSN,
    release: packageJson.version,
    environment: window.SENTRY_ENVIRONMENT,
    ignoreErrors: ['Permission Denied'],
    integrations: [
      Sentry.reactRouterV6BrowserTracingIntegration({
        useEffect: React.useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes,
      }),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    replaysSessionSampleRate: 0.1, // 10% in production
    replaysOnErrorSampleRate: 1.0, // 100% when sampling sessions where errors occur
  });
}

const root = createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
