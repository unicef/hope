import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface VolumeByDeliveryMechanismProps {
  data: AllChartsQuery['chartVolumeByDeliveryMechanism'];
}
export const VolumeByDeliveryMechanism = ({
  data,
}: VolumeByDeliveryMechanismProps): React.ReactElement => {
  if (!data) return null;
  const chartData = {
    labels: data?.labels,
    datasets: [
      {
        backgroundColor: [
          '#03867B',
          '#004D46',
          '#80CB26',
          '#FFAA1D',
          '#FFE498',
        ],
        data: data?.datasets[0]?.data,
      },
    ],
  };
  const options = {
    cutoutPercentage: 80,
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
      }
    },
  };

  return <Doughnut data={chartData} options={options} />;
};
