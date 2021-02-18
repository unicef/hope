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
        barPercentage: 0.4,
        label: data?.datasets[0]?.label,
        backgroundColor: '#00A9FB',
        data: data?.datasets[0]?.data,
      },
      {
        barPercentage: 0.4,
        label: data?.datasets[1]?.label,
        backgroundColor: '#023F90',
        data: data?.datasets[1]?.data,
      },
    ],
  };

  const options = {
    barPercentage: 0.1,
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
      }
    },
    scales: {
      xAxes: [
        {
          stacked: true,
          ticks: {
            stepSize: 1,
          },
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

  return <HorizontalBar data={chartData} options={options} />;
};
