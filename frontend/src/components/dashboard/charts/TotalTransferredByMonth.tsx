import * as React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  formatCurrencyWithSymbol,
  formatThousands,
  getPercentage,
} from '@utils/utils';
import { AllChartsQuery } from '@generated/graphql';

interface TotalTransferredByMonthProps {
  data: AllChartsQuery['chartTotalTransferredByMonth'];
}

export function TotalTransferredByMonth({
  data,
}: TotalTransferredByMonthProps): React.ReactElement {
  if (!data) return null;

  const chartdata: any = {
    labels: data.labels,
    datasets: [
      {
        barPercentage: 0.3,
        label: data.datasets[0]?.label,
        backgroundColor: '#C3D1D8',
        data: [...(data.datasets[0]?.data || [])],
        stack: 3,
      },
      {
        barPercentage: 0.3,
        label: data.datasets[1]?.label,
        backgroundColor: '#FFAA1D',
        data: [...(data.datasets[1]?.data || [])],
        stack: 3,
      },
      {
        barPercentage: 0.3,
        label: data.datasets[2]?.label,
        backgroundColor: '#03867B',
        data: [...(data.datasets[2]?.data || [])],
        stack: 3,
      },
    ],
  };

  const options: any = {
    plugins: {
      legend: {
        labels: {
          padding: 40,
        },
      },
      tooltip: {
        mode: 'point',
        callbacks: {
          label: (context) => {
            const tooltipItem = context.raw;
            const tooltipData = context.chart.data;
            if (!context.datasetIndex) {
              // no percentage for previous transfers value
              return ` ${
                tooltipData.datasets[context.datasetIndex].label
              }: ${formatCurrencyWithSymbol(tooltipItem.y)}`;
            }
            return ` ${
              tooltipData.datasets[context.datasetIndex].label
            }: ${formatCurrencyWithSymbol(tooltipItem.y)} (${getPercentage(
              tooltipItem.y,
              tooltipData.datasets[1].data[context.dataIndex] +
                tooltipData.datasets[2].data[context.dataIndex],
            )})`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        title: {
          display: true,
          text: 'USD',
        },
        position: 'right',
        beginAtZero: true,
        ticks: {
          callback: formatThousands,
        },
      },
    },
  };

  return (
    <div style={{ height: '400px' }}>
      <Bar data={chartdata} options={options} />
    </div>
  );
}
