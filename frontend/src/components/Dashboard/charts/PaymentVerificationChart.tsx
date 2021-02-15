import React from 'react';
import { HorizontalBar } from 'react-chartjs-2';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface PaymentVerificationChartProps {
  data: AllChartsQuery['chartPaymentVerification'];
}
export const PaymentVerificationChart = ({
  data,
}: PaymentVerificationChartProps): React.ReactElement => {
  const chartData = {
    datasets: [
      {
        barPercentage: 0.1,
        label: `Received ${(data?.datasets[1]?.data[0] * 100).toFixed(0)}%`,
        backgroundColor: '#8BD241',
        data: data?.datasets[1]?.data,
      },
      {
        barPercentage: 0.1,
        label: `Received with Issues ${(
          data?.datasets[3]?.data[0] * 100
        ).toFixed(0)}%`,
        backgroundColor: '#FDE8AC',
        data: data?.datasets[3]?.data,
      },
      {
        barPercentage: 0.1,
        label: `Not received ${(data?.datasets[2]?.data[0] * 100).toFixed(0)}%`,
        backgroundColor: '#E02020',
        data: data?.datasets[2]?.data,
      },
      {
        barPercentage: 0.1,
        label: `Not responded ${(data?.datasets[0]?.data[0] * 100).toFixed(
          0,
        )}%`,
        backgroundColor: '#C3D1D8',
        data: data?.datasets[0]?.data,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
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
            min: 0,
            max: 1,
            callback: (value) => `${(value * 100).toFixed(0)}%`,
          },
          gridLines: {
            display: false,
          },
          stacked: true,
        },
      ],
      yAxes: [
        {
          gridLines: {
            display: false,
          },
          stacked: true,
          position: 'right',
        },
      ],
    },
  };

  return <HorizontalBar data={chartData} options={options} />;
};
