import { Box } from '@mui/material';
import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { formatNumber, getPercentage } from '../../../utils/utils';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface PaymentsChartProps {
  data: AllChartsQuery['chartPayment'];
}
export function PaymentsChart({
  data,
}: PaymentsChartProps): React.ReactElement {
  if (!data) return null;

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        backgroundColor: ['#3363A5', '#FFAA1D'],
        data: [...data.datasets[0]?.data],
      },
    ],
  };
  const options = {
    cutoutPercentage: 80,
    legend: {
      labels: {
        padding: 25,
        boxWidth: 10,
      },
    },
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: 20,
    },
    tooltips: {
      mode: 'point',
      callbacks: {
        label: (tooltipItem, tooltipData) => ` ${tooltipData.labels[tooltipItem.index]}: ${formatNumber(
          tooltipData.datasets[0].data[tooltipItem.index],
        )} (${getPercentage(
          tooltipData.datasets[0].data[tooltipItem.index],
          tooltipData.datasets[0].data.reduce((acc, curr) => acc + curr, 0),
        )})`,
      },
    },
  };

  return (
    <Box mt={6} height="300px">
      <Doughnut data={chartData} options={options} />
    </Box>
  );
}
