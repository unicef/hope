import React from 'react';
import { HorizontalBar } from 'react-chartjs-2';
import { formatThousands } from '../../../utils/utils';
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
        categoryPercentage: 0.5,
        maxBarThickness: 20,
        label: data?.datasets[0]?.label,
        backgroundColor: '#00A9FB',
        data: data?.datasets[0]?.data,
      },
      {
        categoryPercentage: 0.5,
        maxBarThickness: 20,
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
        padding: 40,
      },
    },
    tooltips: {
      mode: 'point',
    },
    scales: {
      xAxes: [
        {
          position: 'top',
          stacked: true,
          ticks: {
            beginAtZero: true,
            stepSize: 1,
            callback: formatThousands,
            suggestedMax: Math.max(...data.datasets[2].data) + 1,
          },
        },
      ],
      yAxes: [
        {
          position: 'left',
          stacked: true,
          gridLines: {
            display: false,
          },
        },
      ],
    },
  };

  return <HorizontalBar data={chartData} options={options} />;
};
