import React from 'react';
import {HorizontalBar} from 'react-chartjs-2';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import {formatNumber, formatThousands, getPercentage,} from '../../../utils/utils';
import {AllChartsQuery} from '../../../__generated__/graphql';

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
        barPercentage: 0.4,
        label: data.datasets[0]?.label,
        backgroundColor: '#FFAA1D',
        data: [...data.datasets[0]?.data],
        stack: 2,
      },
      {
        barPercentage: 0.4,
        label: data.datasets[1]?.label,
        backgroundColor: '#C3D1D8',
        data: [...data.datasets[1]?.data],
        stack: 2,
      },
    ],
  };

  const options = {
    legend: {
      labels: {
        padding: 40,
      },
    },
    tooltips: {
      mode: 'point',
      callbacks: {
        label: (tooltipItem, tooltipData) => {
          return ` ${
            tooltipData.datasets[tooltipItem.datasetIndex].label
          }: ${formatNumber(tooltipItem.xLabel)} (${getPercentage(
            tooltipItem.xLabel,
            data.datasets[2].data[tooltipItem.index],
          )})`;
        },
      },
    },
    scales: {
      xAxes: [
        {
          position: 'top',
          ticks: {
            beginAtZero: true,
            callback: formatThousands,
            precision: 0,
            suggestedMax: Math.max(...data.datasets[2].data) + 10,
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
    plugins: {
      datalabels: {
        align: 'end',
        anchor: 'end',
        formatter: (value, { datasetIndex, dataIndex }) => {
          if (datasetIndex === 1 && data.datasets[2].data[dataIndex]) {
            return formatNumber(data.datasets[2].data[dataIndex]);
          }
          return null;
        },
      },
    },
  };

  return (
    <HorizontalBar
      data={chartData}
      options={options}
      plugins={[ChartDataLabels]}
    />
  );
};
