import { Box, Button } from '@material-ui/core';
import React, { useState } from 'react';
import { HorizontalBar } from 'react-chartjs-2';

export const TotalAmountPlannedAndTransferredByCountryChart = (): React.ReactElement => {
  const [showAll, setShowAll] = useState(false);
  const matchDataSize = (data: number[] | string[]): number[] | string[] => {
    return showAll ? data : data.slice(0, 5);
  };
  const labels = [
    'Nigeria',
    'Ethiopia',
    'Egypt',
    'DR Congo',
    'South Africa',
    'Tanzania',
    'Kenya',
    'Uganda',
    'Algieria',
    'Sudan',
  ];

  const plannedAmountData = [10, 10, 11, 12, 12, 12, 12, 10, 11, 12];
  const actualCashTransferredData = [3, 10, 6, 7, 6, 8, 9, 10, 11, 12];
  const actualVoucherTransferredData = [6, 16, 11, 9, 6, 11, 0, 9, 6, 9];
  const data = {
    labels: matchDataSize(labels),
    datasets: [
      {
        barPercentage: 0.8,
        label: 'Planned amount',
        backgroundColor: '#CCDADE',
        data: matchDataSize(plannedAmountData),
        stack: 1,
      },
      {
        barPercentage: 0.8,
        label: 'Actual cash transferred',
        backgroundColor: '#03867B',
        data: matchDataSize(actualCashTransferredData),
        stack: 2,
      },
      {
        barPercentage: 0.8,
        label: 'Actual voucher transferred',
        backgroundColor: '#FFAA1D',
        data: matchDataSize(actualVoucherTransferredData),
        stack: 2,
      },
    ],
  };

  const options = {
    barPercentage: 0.1,
    legend: {
      position: 'bottom',
    },
    tooltips: {
      mode: 'point',
    },
    scales: {
      xAxes: [
        {
          scaleLabel: {
            display: true,
            labelString: 'USD',
          },
          stacked: true,
          position: 'top',
        },
      ],
      yAxes: [
        {
          stacked: true,
          position: 'left',
        },
      ],
    },
  };

  return (
    <Box flexDirection='column'>
      <HorizontalBar data={data} options={options} />
      <Button color='primary' onClick={() => setShowAll(!showAll)}>
        {showAll ? 'HIDE' : 'SHOW ALL'}
      </Button>
    </Box>
  );
};
