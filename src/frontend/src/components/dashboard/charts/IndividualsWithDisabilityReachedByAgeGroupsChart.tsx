import * as React from 'react';
import { Bar } from 'react-chartjs-2';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { formatNumber, formatThousands, getPercentage } from '@utils/utils';
import { AllChartsQuery } from '@generated/graphql';

interface IndividualsWithDisabilityReachedByAgeGroupsChartProps {
  data: AllChartsQuery['chartIndividualsWithDisabilityReachedByAge'];
}

export const IndividualsWithDisabilityReachedByAgeGroupsChart = ({
  data,
}: IndividualsWithDisabilityReachedByAgeGroupsChartProps): React.ReactElement => {
  if (!data) return null;

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: data.datasets[0]?.label,
        backgroundColor: '#FFAA1D',
        data: [...(data.datasets[0]?.data || [])],
      },
      {
        label: data.datasets[1]?.label,
        backgroundColor: '#C3D1D8',
        data: [...(data.datasets[1]?.data || [])],
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    scales: {
      x: {
        type: 'linear',
        position: 'top',
        min: 0,
        max: Math.max(...data.datasets[2].data) + 10,
        ticks: {
          callback: formatThousands,
          precision: 0,
        },
        grid: {
          display: false,
        },
      } as any,
      y: {
        type: 'category',
        position: 'left',
        grid: {
          display: false,
        },
      } as any,
    },
    plugins: {
      datalabels: {
        align: 'end',
        anchor: 'end',
        formatter: (_, context) => {
          const dataIndex = context.dataIndex;
          const datasetIndex = context.datasetIndex;
          if (datasetIndex === 1 && data.datasets[2].data[dataIndex]) {
            return formatNumber(data.datasets[2].data[dataIndex]);
          }
          return null;
        },
      },
      legend: {
        labels: {
          padding: 40,
        },
      },
      tooltip: {
        mode: 'point',
        callbacks: {
          label: (context) => {
            const tooltipItem = context.parsed;
            const tooltipData = context.chart.data;
            return ` ${
              tooltipData.datasets[context.datasetIndex].label
            }: ${formatNumber(tooltipItem.x)} (${getPercentage(
              tooltipItem.x,
              data.datasets[2].data[context.dataIndex],
            )})`;
          },
        },
      },
    },
  } as any;
  return (
    <div style={{ height: '400px' }}>
      <Bar data={chartData} options={options} plugins={[ChartDataLabels]} />
    </div>
  );
};
