import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface GrievancesChartProps {
  data: AllChartsQuery['chartGrievances'];
}
export const GrievancesChart = ({
  data,
}: GrievancesChartProps): React.ReactElement => {
  const chartData = {
    labels: data?.labels,
    datasets: [
      {
        backgroundColor: ['#80CB26', '#FFE9AC', '#FFAA1D', '#E02020'],
        data: data?.datasets[0]?.data,
      },
    ],
  };
  const options = {
    cutoutPercentage: 80,
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
      }
    },
  };

  return <Doughnut data={chartData} options={options} />;
};
