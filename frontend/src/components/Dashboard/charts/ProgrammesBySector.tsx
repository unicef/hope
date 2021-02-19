import React from 'react';
import { HorizontalBar } from 'react-chartjs-2';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface ProgrammesBySectorProps {
  data: AllChartsQuery['chartProgrammesBySector'];
}
export const ProgrammesBySector = ({
  data,
}: ProgrammesBySectorProps): React.ReactElement => {
  if (!data) return null;
  const chartData = {
    labels: data?.labels,
    datasets: [
      {
        barPercentage: data.datasets[0].data.length < 3 ? 0.2 : 0.3,
        label: data?.datasets[0]?.label,
        backgroundColor: '#00A9FB',
        data: data?.datasets[0]?.data,
      },
      {
        barPercentage: data.datasets[0].data.length < 3 ? 0.2 : 0.3,
        label: data?.datasets[1]?.label,
        backgroundColor: '#023F90',
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
          position: 'top',
          stacked: true,
          ticks: {
            beginAtZero: true,
            stepSize: 1,
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
          position: 'left',
          stacked: true,
        },
      ],
    },
  };

  return <HorizontalBar data={chartData} options={options} />;
};
