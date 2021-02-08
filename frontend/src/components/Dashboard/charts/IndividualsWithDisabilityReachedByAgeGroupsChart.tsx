import React from 'react';
import { HorizontalBar } from 'react-chartjs-2';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface IndividualsWithDisabilityReachedByAgeGroupsChartProps {
  data: AllChartsQuery['chartIndividualsWithDisabilityReachedByAge'];
}

export const IndividualsWithDisabilityReachedByAgeGroupsChart = ({
  data,
}: IndividualsWithDisabilityReachedByAgeGroupsChartProps): React.ReactElement => {
  const labels = data?.labels;
  const chartData = {
    labels,
    datasets: [
      {
        barPercentage: 0.8,
        label: data?.datasets[0]?.label,
        backgroundColor: '#FFAA1D',
        data: data?.datasets[0]?.data,
      },
      {
        barPercentage: 0.8,
        label: data?.datasets[1]?.label,
        backgroundColor: '#C3D1D8',
        data: data?.datasets[1]?.data,
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

  return <HorizontalBar data={chartData} options={options} />;
};
