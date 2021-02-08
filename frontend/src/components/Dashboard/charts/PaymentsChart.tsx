import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface PaymentsChartProps {
  data: AllChartsQuery['chartPayment'];
}
export const PaymentsChart = ({
  data,
}: PaymentsChartProps): React.ReactElement => {
  const chartData = {
    labels: data?.labels,
    datasets: [
      {
        backgroundColor: ['#3363A5', '#FFAA1D'],
        data: data?.datasets[0]?.data,
      },
    ],
  };
  const options = {
    cutoutPercentage: 80,
    legend: {
      position: 'bottom',
    },
  };

  return <Doughnut data={chartData} options={options} />;
};
