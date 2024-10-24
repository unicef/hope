import { Box } from '@mui/material';
import * as React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { formatNumber, getPercentage } from '@utils/utils';
import { AllChartsQuery } from '@generated/graphql';

interface GrievancesChartProps {
  data: AllChartsQuery['chartGrievances'];
}
export function GrievancesChart({
  data,
}: GrievancesChartProps): React.ReactElement {
  if (!data) return null;

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        backgroundColor: ['#80CB26', '#FFE9AC', '#FFAA1D', '#E02020'],
        data: [...(data.datasets[0]?.data || [])],
      },
    ],
  };
  const options = {
    cutoutPercentage: 80,
    legend: {
      align: 'start',
      labels: {
        boxWidth: 10,
        padding: 15,
      },
    },
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: {
        top: 20,
        bottom: 20,
      },
    },
    tooltips: {
      mode: 'point',
      callbacks: {
        label: (tooltipItem, tooltipData) =>
          ` ${tooltipData.labels[tooltipItem.index]}: ${formatNumber(
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
