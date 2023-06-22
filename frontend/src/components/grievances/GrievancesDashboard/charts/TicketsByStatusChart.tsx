import { Box } from '@material-ui/core';
import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { AllGrievanceDashboardChartsQuery } from '../../../../__generated__/graphql';

interface TicketsByStatusChartProps {
  data: AllGrievanceDashboardChartsQuery['ticketsByCategory'];
}

export const TicketsByStatusChart = ({
  data,
}: TicketsByStatusChartProps): React.ReactElement => {
  if (!data) return null;

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        backgroundColor: [
          '#F5801A',
          '#023E90',
          '#13CB17',
          '#FF0200',
          '#6D4C41',
          '#4F616B',
        ],
        data: [...data.datasets[0]?.data],
      },
    ],
  };
  const options = {
    cutoutPercentage: 80,
    responsive: true,
    maintainAspectRatio: false,
    legend: {
      position: 'bottom',
      align: 'center',
      labels: {
        usePointStyle: true,
      },
    },
  };

  return (
    <Box mt={6} height='300px'>
      <Doughnut data={chartData} options={options} />
    </Box>
  );
};
