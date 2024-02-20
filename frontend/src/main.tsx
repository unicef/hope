import * as React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import * as Sentry from '@sentry/react';
import { Chart as ChartJS } from 'chart.js';
import packageJson from '../package.json';
import setupInternalization from './i18n';
import * as serviceWorker from './serviceWorker';
import { FONT } from './theme';
import { App } from './App';

ChartJS.defaults.font.family = FONT;
ChartJS.defaults.plugins.tooltip.padding = 12;
ChartJS.defaults.plugins.tooltip.cornerRadius = 2;
ChartJS.defaults.plugins.tooltip.mode = 'point';
ChartJS.defaults.plugins.legend.position = 'bottom';
ChartJS.defaults.plugins.legend.labels.usePointStyle = true;
ChartJS.defaults.plugins.legend.labels.boxWidth = 8;

setupInternalization();
if (process.env.NODE_ENV !== 'development' && process.env.SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    release: packageJson.version,
    environment: process.env.SENTRY_ENVIRONMENT,
    ignoreErrors: ['Permission Denied'],
  });
}

const root = createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
