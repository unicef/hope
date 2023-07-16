import React from 'react';
import { HorizontalBar } from 'react-chartjs-2';
import { formatThousands } from '../../../../utils/utils';
import { AllGrievanceDashboardChartsQuery } from '../../../../__generated__/graphql';

interface TicketsByCategoryChartProps {
  data: AllGrievanceDashboardChartsQuery['ticketsByCategory'];
}
export const TicketsByCategoryChart = ({
  data,
}: TicketsByCategoryChartProps): React.ReactElement => {
  if (!data) return null;

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        categoryPercentage: 0.5,
        maxBarThickness: 20,
        backgroundColor: '#00867B',
        data: [...data.datasets[0]?.data],
        stack: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    legend: {
      display: false,
    },
    tooltips: {
      mode: 'point',
    },
    scales: {
      xAxes: [
        {
          position: 'top',
          ticks: {
            beginAtZero: true,
            stepSize: 1,
            callback: formatThousands,
            suggestedMax: Math.max(...data.datasets[0].data) + 1,
          },
        },
      ],
      yAxes: [
        {
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
