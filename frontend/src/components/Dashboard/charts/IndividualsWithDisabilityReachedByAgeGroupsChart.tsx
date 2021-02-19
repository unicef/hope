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
        barPercentage: 0.4,
        label: data?.datasets[0]?.label,
        backgroundColor: '#FFAA1D',
        data: data?.datasets[0]?.data,
      },
      {
        barPercentage: 0.4,
        label: data?.datasets[1]?.label,
        backgroundColor: '#C3D1D8',
        data: data?.datasets[1]?.data,
      },
    ],
  };

  const options = {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
      },
    },
    scales: {
      xAxes: [
        {
          stacked: true,
          position: 'top',
          ticks: {
            beginAtZero: true,
            callback: (value) => {
              if (parseInt(value, 10) >= 100000) {
                return `${value.toString().slice(0, -3)}k`;
              }
              return value;
            },
          },
        },
      ],
      yAxes: [
        {
          stacked: true,
          position: 'left',
          gridLines: {
            display: false,
          },
        },
      ],
    },
  };

  return <HorizontalBar data={chartData} options={options} />;
};
