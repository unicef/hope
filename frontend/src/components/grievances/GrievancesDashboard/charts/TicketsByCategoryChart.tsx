import * as React from 'react';
import { Bar } from 'react-chartjs-2';
import { formatThousands } from '@utils/utils';
import { AllGrievanceDashboardChartsQuery } from '@generated/graphql';

interface TicketsByCategoryChartProps {
  data: AllGrievanceDashboardChartsQuery['ticketsByCategory'];
}

export function TicketsByCategoryChart({
  data,
}: TicketsByCategoryChartProps): React.ReactElement {
  if (!data) return null;

  const chartData: any = {
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

  const options: any = {
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
    indexAxis: 'y',
  };

  return <Bar data={chartData} options={options} />;
}
