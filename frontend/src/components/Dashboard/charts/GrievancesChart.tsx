import React from 'react';
import { Doughnut } from 'react-chartjs-2';

export const GrievancesChart = (): React.ReactElement => {
  const data = {
    labels: [
      'Resolved',
      'Unresolved',
      'Unresolved for longer than 30 days',
      'Unresolved for longer than 60 days',
    ],
    datasets: [
      {
        backgroundColor: ['#80CB26', '#FFE9AC', '#FFAA1D', '#E02020'],
        data: [40, 20, 10, 30],
      },
    ],
  };
  const options = {
    maintainAspectRatio: false,
    cutoutPercentage: 65,
    legend: {
      position: 'bottom',
    },
  };

  return <Doughnut data={data} options={options} />;
};
