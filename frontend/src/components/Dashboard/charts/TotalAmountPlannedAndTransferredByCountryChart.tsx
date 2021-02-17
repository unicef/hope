import { Box, Button } from '@material-ui/core';
import React, { useState } from 'react';
import { HorizontalBar } from 'react-chartjs-2';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface TotalAmountPlannedAndTransferredByCountryChartProps {
  data: AllChartsQuery['chartTotalTransferredCashByCountry'];
}

export const TotalAmountPlannedAndTransferredByCountryChart = ({
  data,
}: TotalAmountPlannedAndTransferredByCountryChartProps): React.ReactElement => {
  const lessDataCount = 5;
  const [showAll, setShowAll] = useState(false);
  const matchDataSize = (
    dataToSlice: number[] | string[],
  ): number[] | string[] => {
    return showAll ? dataToSlice : dataToSlice.slice(0, lessDataCount);
  };

  const chartData = {
    labels: matchDataSize(data.labels),
    datasets: [
      {
        barPercentage: 0.8,
        label: 'Planned amount',
        backgroundColor: '#CCDADE',
        data: matchDataSize(data.datasets[0].data),
        stack: 1,
      },
      {
        barPercentage: 0.8,
        label: 'Actual cash transferred',
        backgroundColor: '#03867B',
        data: matchDataSize(data.datasets[1].data),
        stack: 2,
      },
      {
        barPercentage: 0.8,
        label: 'Actual voucher transferred',
        backgroundColor: '#FFAA1D',
        data: matchDataSize(data.datasets[2].data),
        stack: 2,
      },
    ],
  };

  const options = {
    barPercentage: 0.1,
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
      }
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
      <HorizontalBar data={chartData} options={options} />
      {data.labels.length <= lessDataCount || (
        <Button color='primary' onClick={() => setShowAll(!showAll)}>
          {showAll ? 'HIDE' : 'SHOW ALL'}
        </Button>
      )}
    </Box>
  );
};
