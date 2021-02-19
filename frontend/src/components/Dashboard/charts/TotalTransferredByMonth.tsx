import React from 'react';
import { Bar } from 'react-chartjs-2';
import { formatCurrencyWithSymbol, getPercentage } from '../../../utils/utils';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface TotalTransferredByMonthProps {
  data: AllChartsQuery['chartTotalTransferredByMonth'];
}
export const TotalTransferredByMonth = ({
  data,
}: TotalTransferredByMonthProps): React.ReactElement => {
  if (!data) return null;
  const chartdata = {
    labels: data?.labels,
    datasets: [
      {
        barPercentage: 0.3,
        label: data?.datasets[0]?.label,
        backgroundColor: '#C3D1D8',
        data: data?.datasets[0]?.data,
      },
      {
        barPercentage: 0.3,
        label: data?.datasets[1]?.label,
        backgroundColor: '#FFAA1D',
        data: data?.datasets[1]?.data,
      },
      {
        barPercentage: 0.3,
        label: data?.datasets[2]?.label,
        backgroundColor: '#03867B',
        data: data?.datasets[2]?.data,
      },
    ],
  };

  const options = {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
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
          stacked: true,
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
          stacked: true,
          position: 'right',
          ticks: {
            beginAtZero: true,
            callback: (value) => {
              if (parseInt(value, 10) >= 100000) {
                return `${value.toString().slice(0, -3)}k`;
              }
              return value;
            },
          },
        },
      ],
    },
  };

  return <Bar data={chartdata} options={options} />;
};
