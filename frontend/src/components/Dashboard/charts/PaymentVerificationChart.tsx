import React from 'react';
import { HorizontalBar } from 'react-chartjs-2';

export const PaymentVerificationChart = (): React.ReactElement => {
  const data = {
    labels: ['Payment Verification'],
    datasets: [
      {
        barPercentage: 0.1,
        label: 'Received',
        backgroundColor: '#8CD241',
        data: [0.38],
      },
      {
        barPercentage: 0.1,
        label: 'Received with Issues',
        backgroundColor: '#FFE9AC',
        data: [0.28],
      },
      {
        barPercentage: 0.1,
        label: 'Not Received',
        backgroundColor: '#FFAA1D',
        data: [0.18],
      },
      {
        barPercentage: 0.1,
        label: 'Not Responded',
        backgroundColor: '#E02020',
        data: [0.16],
      },
    ],
  };

  const options = {
    responsive: true,
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

  return <HorizontalBar data={data} options={options} />;
};
