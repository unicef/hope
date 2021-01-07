import React from 'react';
import { Doughnut } from 'react-chartjs-2';

export const VolumeByDeliveryMechanism = (): React.ReactElement => {
  const data = {
    labels: [
      'Cash in envelope',
      'Deposit to card',
      'Mobile money',
      'Voucher',
      'E-voucher',
    ],
    datasets: [
      {
        backgroundColor: [
          '#03867B',
          '#004D46',
          '#80CB26',
          '#FFAA1D',
          '#FFE498',
        ],
        data: [10, 30, 20, 5, 35],
      },
    ],
  };
  const options = {
    maintainAspectRatio: false,
    cutoutPercentage: 65,
    legend: {
      position: 'bottom',
    },
  };

  return <Doughnut data={data} options={options} />;
};
