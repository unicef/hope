import { Bar } from 'react-chartjs-2';
import { formatThousands } from '@utils/utils';
import { ChartData } from '@restgenerated/models/ChartData';
import { ReactElement } from 'react';

interface TicketsByCategoryChartProps {
  data: ChartData;
}

export const TicketsByCategoryChart = ({
  data,
}: TicketsByCategoryChartProps): ReactElement => {
  if (!data) return null;

  const chartData: any = {
    labels: data.labels,
    datasets: [
      {
        categoryPercentage: 0.5,
        maxBarThickness: 20,
        backgroundColor: '#00867B',
        data: [...(data.datasets[0]?.data || [])],
        stack: 2,
      },
    ],
  };

  const options: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    tooltips: {
      mode: 'point',
    },
    scales: {
      x: {
        position: 'top',
        ticks: {
          beginAtZero: true,
          stepSize: 1,
          callback: formatThousands,
          suggestedMax: Math.max(...data.datasets[0].data) + 1,
        },
      },
      y: {
        position: 'left',
        grid: {
          display: false,
        },
      },
    },
    indexAxis: 'y',
  };

  return (
    <div style={{ height: '400px', width: '100%' }}>
      <Bar data={chartData} options={options} />
    </div>
  );
};
