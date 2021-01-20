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
    labels: data?.labels,
    datasets: [
      {
        barPercentage: 0.1,
        label: data?.datasets[0]?.label,
        backgroundColor: '#8CD241',
        data: data?.datasets[0]?.data,
      },
      {
        barPercentage: 0.1,
        label: data?.datasets[1]?.label,
        backgroundColor: '#FFE9AC',
        data: data?.datasets[1]?.data,
      },
      {
        barPercentage: 0.1,
        label: data?.datasets[2]?.label,
        backgroundColor: '#FFAA1D',
        data: data?.datasets[2]?.data,
      },
      {
        barPercentage: 0.1,
        label: data?.datasets[3]?.label,
        backgroundColor: '#E02020',
        data: data?.datasets[3]?.data,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    legend: {
      position: 'bottom',
    },
    scales: {
      xAxes: [
        {
          ticks: {
            min: 0,
            max: 1,
            callback: (value) => `${(value * 100).toFixed(0)} %`,
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
