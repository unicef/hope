import React from 'react';
import {Bar} from 'react-chartjs-2';
import {formatCurrencyWithSymbol, formatThousands, getPercentage,} from '../../../utils/utils';
import {AllChartsQuery} from '../../../__generated__/graphql';

interface TotalTransferredByMonthProps {
  data: AllChartsQuery['chartTotalTransferredByMonth'];
}
export const TotalTransferredByMonth = ({
  data,
}: TotalTransferredByMonthProps): React.ReactElement => {
  if (!data) return null;

  const chartdata = {
    labels: data.labels,
    datasets: [
      {
        barPercentage: 0.3,
        label: data.datasets[0]?.label,
        backgroundColor: '#C3D1D8',
        data: [...data.datasets[0]?.data],
        stack: 3,
      },
      {
        barPercentage: 0.3,
        label: data.datasets[1]?.label,
        backgroundColor: '#FFAA1D',
        data: [...data.datasets[1]?.data],
        stack: 3,
      },
      {
        barPercentage: 0.3,
        label: data.datasets[2]?.label,
        backgroundColor: '#03867B',
        data: [...data.datasets[2]?.data],
        stack: 3,
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
          if (!tooltipItem.datasetIndex) {
            // no percentage for previous tranfers value
            return ` ${
              tooltipData.datasets[tooltipItem.datasetIndex].label
            }: ${formatCurrencyWithSymbol(tooltipItem.yLabel)}`;
          }
          return ` ${
            tooltipData.datasets[tooltipItem.datasetIndex].label
          }: ${formatCurrencyWithSymbol(tooltipItem.yLabel)} (${getPercentage(
            tooltipItem.yLabel,
            tooltipData.datasets[1].data[tooltipItem.index] +
              tooltipData.datasets[2].data[tooltipItem.index],
          )})`;
        },
      },
    },
    scales: {
      xAxes: [
        {
          gridLines: {
            display: false,
          },
        },
      ],
      yAxes: [
        {
          scaleLabel: {
            display: true,
            labelString: 'USD',
          },
          position: 'right',
          ticks: {
            beginAtZero: true,
            callback: formatThousands,
          },
        },
      ],
    },
  };

  return <Bar data={chartdata} options={options} />;
};
