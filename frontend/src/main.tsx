import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import * as Sentry from '@sentry/react';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import Chart from 'chart.js/auto'; // Import Chart.js correctly
import packageJson from '../package.json';
import setupInternalization from './i18n';
import * as serviceWorker from './serviceWorker';
import { FONT } from './theme';
import { App } from './App';

Chart.register(ChartDataLabels); // Register the plugin

Chart.defaults.font.family = FONT;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 2;
Chart.defaults.plugins.tooltip.mode = 'point';
Chart.defaults.plugins.legend.position = 'bottom';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.boxWidth = 8;

Chart.defaults.plugins.datalabels.font = {
  family: FONT,
};
Chart.defaults.plugins.datalabels.font = () => ({
  weight: 'bold',
});

setupInternalization();
if (process.env.NODE_ENV !== 'development' && process.env.SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    release: packageJson.version,
    environment: process.env.SENTRY_ENVIRONMENT,
    ignoreErrors: ['Permission Denied'],
  });
}

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root'),
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
