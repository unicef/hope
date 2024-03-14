import * as React from 'react';
import { Bar } from 'react-chartjs-2';
import { formatThousands } from '@utils/utils';
import { AllChartsQuery } from '@generated/graphql';

interface ProgrammesBySectorProps {
  data: AllChartsQuery['chartProgrammesBySector'];
}

export const ProgrammesBySector = ({
  data,
}: ProgrammesBySectorProps): React.ReactElement => {
  if (!data) return null;

  const chartData: any = {
    labels: data.labels,
    datasets: [
      {
        categoryPercentage: 0.5,
        maxBarThickness: 20,
        label: data.datasets[0]?.label,
        backgroundColor: '#00A9FB',
        data: [...(data.datasets[0]?.data || [])],
        stack: 2,
      },
      {
        categoryPercentage: 0.5,
        maxBarThickness: 20,
        label: data.datasets[1]?.label,
        backgroundColor: '#023F90',
        data: [...(data.datasets[1]?.data || [])],
        stack: 2,
      },
    ],
  };

  const options: any = {
    indexAxis: 'y',
    responsive: false,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 40,
        },
      },
      tooltip: {
        mode: 'point',
      },
    },
    scales: {
      x: {
        position: 'top',
        ticks: {
          beginAtZero: true,
          stepSize: 1,
          callback: formatThousands,
          suggestedMax: Math.max(...data.datasets[2].data) + 1,
        },
      },
      y: {
        position: 'left',
        grid: {
          display: false,
        },
      },
    },
  };

  return (
    <div style={{ height: '400px' }}>
      <Bar data={chartData} options={options} />
    </div>
  );
};
