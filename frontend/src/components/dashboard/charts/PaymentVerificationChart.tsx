import { Box } from '@mui/material';
import * as React from 'react';
import { Bar } from 'react-chartjs-2';
import { AllChartsQuery } from '@generated/graphql';
import type { ChartData, ChartOptions } from 'chart.js';

interface PaymentVerificationChartProps {
  data: AllChartsQuery['chartPaymentVerification']['datasets'];
}

type DatasetTypes =
  | 'RECEIVED'
  | 'PENDING'
  | 'NOT RECEIVED'
  | 'RECEIVED WITH ISSUES';

type Dataset = {
  [key in DatasetTypes]: Array<number>;
};

export function PaymentVerificationChart({
  data,
}: PaymentVerificationChartProps): React.ReactElement {
  const datasets = data.reduce(
    (previousValue, currentValue) => ({
      ...previousValue,
      [currentValue.label]: currentValue.data,
    }),
    {},
  ) as Dataset;

  const convertToPercent = (dataset: Array<number>): string =>
    `${(dataset[0] * 100).toFixed(0)}%`;

  const chartData: ChartData<'bar'> = {
    labels: [''],
    datasets: [
      {
        categoryPercentage: 0.5,
        stack: '4',
        label: `Received - ${convertToPercent(datasets.RECEIVED)}`,
        backgroundColor: '#8BD241',
        data: [...datasets.RECEIVED],
      },
      {
        categoryPercentage: 0.5,
        stack: '4',
        label: `Received with Issues - ${convertToPercent(
          datasets['RECEIVED WITH ISSUES'],
        )}`,
        backgroundColor: '#FDE8AC',
        data: [...datasets['RECEIVED WITH ISSUES']],
      },
      {
        categoryPercentage: 0.5,
        stack: '4',
        label: `Not received - ${convertToPercent(datasets['NOT RECEIVED'])}`,
        backgroundColor: '#E02020',
        data: [...datasets['NOT RECEIVED']],
      },
      {
        categoryPercentage: 0.5,
        stack: '4',
        label: `Not responded - ${convertToPercent(datasets.PENDING)}`,
        backgroundColor: '#C3D1D8',
        data: [...datasets.PENDING],
      },
    ],
  };

  const options: ChartOptions<'bar'> = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 30,
        },
      },
      tooltip: {
        mode: 'point',
        callbacks: {
          title: () => '',
          label: (context) => context.dataset.label,
        },
      },
    },
    scales: {
      x: {
        ticks: {
          callback: () => '',
        },
        grid: {
          display: false,
        },
      },
      y: {
        grid: {
          display: false,
        },
        position: 'right',
      },
    },
  };

  return (
    <Box height="180px">
      <Bar data={chartData} options={options} />
    </Box>
  );
}
