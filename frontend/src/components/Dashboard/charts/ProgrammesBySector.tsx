import React from 'react';
import { Bar } from 'react-chartjs-2';

export const ProgrammesBySector = (): React.ReactElement => {
  const data = {
    labels: [
      'Child Protection',
      'Education',
      'Gender',
      'Health',
      'HIV/AIDS',
      'Multi Purpose',
      'Nutrition',
      'Social Policy',
      'WASH',
      'Name',
    ],
    datasets: [
      {
        barPercentage: 0.4,
        label: 'Programmes',
        backgroundColor: '#00A9FB',
        data: [9, 10, 6, 7, 6, 8, 9, 10, 11, 12],
      },
      {
        barPercentage: 0.4,
        label: 'Programmes with Cash+',
        backgroundColor: '#023F90',
        data: [12, 16, 11, 9, 6, 11, 0, 9, 6, 9],
      },
    ],
  };

  const options = {
    barPercentage: 0.1,
    legend: {
      position: 'bottom',
    },
    scales: {
      xAxes: [
        {
          stacked: true,
        },
      ],
      yAxes: [
        {
          stacked: true,
          position: 'right',
        },
      ],
    },
  };

  return <Bar data={data} options={options} />;
};
