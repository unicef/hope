import React from 'react';
import { HorizontalBar } from 'react-chartjs-2';

export const IndividualsWithDisabilityReachedByAgeGroupsChart = (): React.ReactElement => {
  const labels = [
    'Females 0-5',
    'Females 6-11',
    'Females 12-17',
    'Females 18-59',
    'Females 60+',
    'Males 0-5',
    'Males 6-11',
    'Males 12-17',
    'Males 18-59',
    'Males 60+',
  ];

  const withDisabilityData = [10, 10, 11, 12, 12, 12, 12, 10, 11, 12];
  const withoutDisabilityData = [3, 10, 6, 7, 6, 8, 9, 10, 11, 12];

  const data = {
    labels,
    datasets: [
      {
        barPercentage: 0.8,
        label: 'with disability',
        backgroundColor: '#FFAA1D',
        data: withDisabilityData,
      },
      {
        barPercentage: 0.8,
        label: 'without disability',
        backgroundColor: '#C3D1D8',
        data: withoutDisabilityData,
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
          position: 'top',
        },
      ],
      yAxes: [
        {
          stacked: true,
          position: 'left',
        },
      ],
    },
  };

  return <HorizontalBar data={data} options={options} />;
};
