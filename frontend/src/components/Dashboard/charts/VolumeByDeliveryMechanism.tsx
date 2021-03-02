import { Box } from '@material-ui/core';
import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { formatCurrencyWithSymbol, getPercentage } from '../../../utils/utils';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface VolumeByDeliveryMechanismProps {
  data: AllChartsQuery['chartVolumeByDeliveryMechanism'];
}
export const VolumeByDeliveryMechanism = ({
  data,
}: VolumeByDeliveryMechanismProps): React.ReactElement => {
  if (!data) return null;

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        backgroundColor: [
          '#05433D',
          '#19C1AD',
          '#76C42E',
          '#FEB23D',
          '#0F7A6F',
          '#92E5DD',
          '#B7E18B',
          '#FEE6A6',
          '#FEb6A6',
          '#FE6Ab6',
          '#12c4f3',
          '#FEa26D',
          '#FF723D',
        ],
        data: [...data.datasets[0]?.data],
      },
    ],
  };

  const options = {
    cutoutPercentage: 80,
    legend: {
      align: 'start',
      labels: {
        boxWidth: 10,
        padding: data.datasets[0]?.data.length < 4 ? 30 : 15,
      },
    },
    responsive: true,
    maintainAspectRatio: false,
    layout: {
      padding: {
        top: 20,
        bottom: 0,
      },
    },
    tooltips: {
      mode: 'point',
      callbacks: {
        label: (tooltipItem, tooltipData) => {
          return ` ${
            tooltipData.labels[tooltipItem.index]
          } ${formatCurrencyWithSymbol(
            tooltipData.datasets[0].data[tooltipItem.index],
          )} (${getPercentage(
            tooltipData.datasets[0].data[tooltipItem.index],
            tooltipData.datasets[0].data.reduce((acc, curr) => acc + curr, 0),
          )})`;
        },
      },
    },
  };

  return (
    <Box mt={6} height='375px'>
      <Doughnut data={chartData} options={options} />
    </Box>
  );
};
