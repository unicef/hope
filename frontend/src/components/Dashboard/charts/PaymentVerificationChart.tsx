import { Box } from '@material-ui/core';
import React from 'react';
import { HorizontalBar } from 'react-chartjs-2';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface PaymentVerificationChartProps {
  data: AllChartsQuery['chartPaymentVerification'];
}
export const PaymentVerificationChart = ({
  data,
}: PaymentVerificationChartProps): React.ReactElement => {
  if (!data) return null;

  const chartData = {
    datasets: [
      {
        categoryPercentage: 0.5,
        label: `Received - ${(data.datasets[1]?.data[0] * 100).toFixed(0)}%`,
        backgroundColor: '#8BD241',
        data: [...data.datasets[1]?.data],
        stack: 4,
      },
      {
        categoryPercentage: 0.5,
        label: `Received with Issues - ${(
          data.datasets[3]?.data[0] * 100
        ).toFixed(0)}%`,
        backgroundColor: '#FDE8AC',
        data: [...data.datasets[3]?.data],
        stack: 4,
      },
      {
        categoryPercentage: 0.5,
        label: `Not received - ${(data.datasets[2]?.data[0] * 100).toFixed(
          0,
        )}%`,
        backgroundColor: '#E02020',
        data: [...data.datasets[2]?.data],
        stack: 4,
      },
      {
        categoryPercentage: 0.5,
        label: `Not responded - ${(data.datasets[0]?.data[0] * 100).toFixed(
          0,
        )}%`,
        backgroundColor: '#C3D1D8',
        data: [...data.datasets[0]?.data],
        stack: 4,
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
