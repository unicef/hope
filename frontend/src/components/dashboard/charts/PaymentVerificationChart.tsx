import { Box } from '@material-ui/core';
import React from 'react';
import { HorizontalBar } from 'react-chartjs-2';
import { AllChartsQuery } from '../../../__generated__/graphql';

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

export const PaymentVerificationChart = ({
  data,
}: PaymentVerificationChartProps): React.ReactElement => {
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
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    legend: {
      position: 'bottom',
      labels: {
        padding: 30,
      },
    },
    tooltips: {
      mode: 'point',
      callbacks: {
        title: () => '',
        label: (tooltipItem, dataArgs) =>
          dataArgs.datasets[tooltipItem.datasetIndex].label,
      },
    },
    scales: {
      xAxes: [
        {
          ticks: {
            callback: () => '',
          },
          gridLines: {
            display: false,
          },
        },
      ],
      yAxes: [
        {
          gridLines: {
            display: false,
          },
          position: 'right',
        },
      ],
    },
  };

  return (
    <Box height='150px'>
      <HorizontalBar data={chartData} options={options} />
    </Box>
  );
};
