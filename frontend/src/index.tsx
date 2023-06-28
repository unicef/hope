import React from 'react';
import ReactDOM from 'react-dom';
import * as Sentry from '@sentry/react';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import Chart from 'chart.js';
import packageJson from '../package.json';
import setupInternalization from './i18n';
import { App } from './App';
import * as serviceWorker from './serviceWorker';
import { FONT } from './theme';

Chart.plugins.unregister(ChartDataLabels);
Chart.defaults.global.defaultFontFamily = FONT;
Chart.defaults.global.tooltips.xPadding = 12;
Chart.defaults.global.tooltips.yPadding = 12;
Chart.defaults.global.tooltips.cornerRadius = 2;
Chart.defaults.global.tooltips.mode = 'point';
Chart.defaults.global.legend.position = 'bottom';
Chart.defaults.global.legend.labels.usePointStyle = true;
Chart.defaults.global.legend.labels.boxWidth = 8;

Chart.defaults.global.plugins.datalabels.font.family = FONT;
Chart.defaults.global.plugins.datalabels.font.weight = 'bold';

setupInternalization();
if (process.env.NODE_ENV !== 'development' && (window as any).config.SENTRY_DSN)
  Sentry.init({
    dsn: (window as any).config.SENTRY_DSN,
    release: packageJson.version,
    environment: (window as any).config.SENTRY_ENVIRONMENT,
    ignoreErrors: ['Permission Denied'],
  });

ReactDOM.render(<App />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
