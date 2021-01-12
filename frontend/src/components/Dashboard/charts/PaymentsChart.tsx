import React from 'react';
import { Doughnut } from 'react-chartjs-2';

export const PaymentsChart = (): React.ReactElement => {
  const data = {
    labels: ['Successful Payments', 'Unsuccessful Payments'],
    datasets: [
      {
        backgroundColor: ['#3363A5', '#FFAA1D'],
        data: [80, 20],
      },
    ],
  };
  const options = {
    cutoutPercentage: 80,
    legend: {
      position: 'bottom',
    },
  };

  return <Doughnut data={data} options={options} />;
};
