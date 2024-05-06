import { Box } from '@mui/material';
import * as React from 'react';
import { Bar } from 'react-chartjs-2';
import { AllChartsQuery } from '@generated/graphql';

interface PaymentVerificationChartProps {
  data: AllChartsQuery['chartPaymentVerification'];
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
  if (!data) return null;

  const datasets = data.datasets.reduce(
    (previousValue, currentValue) => ({
      ...previousValue,
      [currentValue.label]: currentValue.data,
    }),
    {},
  ) as Dataset;

  const convertToPercent = (dataset: Array<number>): string =>
    `${(dataset[0] * 100).toFixed(0)}%`;

  const defaults = {
    categoryPercentage: 0.5,
    stack: 4,
  };

  const chartData = {
    datasets: [
      {
        ...defaults,
        label: `Received - ${convertToPercent(datasets.RECEIVED)}`,
        backgroundColor: '#8BD241',
        data: [...datasets.RECEIVED],
      },
      {
        ...defaults,
        label: `Received with Issues - ${convertToPercent(
          datasets['RECEIVED WITH ISSUES'],
        )}`,
        backgroundColor: '#FDE8AC',
        data: [...datasets['RECEIVED WITH ISSUES']],
      },
      {
        ...defaults,
        label: `Not received - ${convertToPercent(datasets['NOT RECEIVED'])}`,
        backgroundColor: '#E02020',
        data: [...datasets['NOT RECEIVED']],
      },
      {
        ...defaults,
        label: `Not responded - ${convertToPercent(datasets.PENDING)}`,
        backgroundColor: '#C3D1D8',
        data: [...datasets.PENDING],
      },
    ],
  } as any;

  const options = {
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
  } as any;

  return (
    <Box height="150px">
      <Bar data={chartData} options={options} />
    </Box>
  );
}
