import React from 'react';
import { Doughnut } from 'react-chartjs-2';

export const IndividualsReachedByAgeAndGenderGroupsChart = (): React.ReactElement => {
  const data = {
    labels: [
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
    ],
    datasets: [
      {
        backgroundColor: [
          '#5F02CF',
          '#9F66E2',
          '#BF99EB',
          '#DFCCF5',
          '#EFE4F9',
          '#1D6A64',
          '#8DB4B1',
          '#3BBAB2',
          '#B1E3E0',
          '#D2E0E0',
        ],
        data: [5, 7, 10, 10, 12, 12, 14, 15, 15, 20],
      },
    ],
  };
  const options = {
    cutoutPercentage: 65,
    legend: {
      position: 'bottom',
    },
  };

  return <Doughnut data={data} options={options} />;
};
