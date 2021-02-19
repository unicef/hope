import { Box, Button } from '@material-ui/core';
import React, { useState } from 'react';
import { HorizontalBar } from 'react-chartjs-2';
import { formatCurrencyWithSymbol, getPercentage } from '../../../utils/utils';
import { GlobalAreaChartsQuery } from '../../../__generated__/graphql';

interface TotalAmountTransferredByCountryChartProps {
  data: GlobalAreaChartsQuery['chartTotalTransferredCashByCountry'];
}

export const TotalAmountTransferredByCountryChart = ({
  data,
}: TotalAmountTransferredByCountryChartProps): React.ReactElement => {
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
        label: data.datasets[0].label,
        backgroundColor: '#03867B',
        data: matchDataSize(data.datasets[0].data),
        stack: 2,
      },
      {
        barPercentage: 0.8,
        label: data.datasets[1].label,
        backgroundColor: '#FFAA1D',
        data: matchDataSize(data.datasets[1].data),
        stack: 2,
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
          return ` ${
            tooltipData.datasets[tooltipItem.datasetIndex].label
          }: ${formatCurrencyWithSymbol(tooltipItem.xLabel)} (${getPercentage(
            tooltipItem.xLabel,
            tooltipData.datasets[0].data[tooltipItem.index] +
              tooltipData.datasets[1].data[tooltipItem.index],
          )})`;
        },
      },
    },
    scales: {
      xAxes: [
        {
          scaleLabel: {
            display: true,
            labelString: 'USD',
          },
          position: 'top',
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
      yAxes: [
        {
          barPercentage: data.datasets[0].data.length < 3 ? 0.2 : 0.3,
          position: 'left',
        },
      ],
    },
  };

  return (
    <Box flexDirection='column'>
      <HorizontalBar data={chartData} options={options} />
      {data.labels.length <= lessDataCount || (
        <Box textAlign='center' mt={4} ml={2} mr={2}>
          <Button
            variant='outlined'
            color='primary'
            onClick={() => setShowAll(!showAll)}
            fullWidth
          >
            {showAll ? 'HIDE' : 'SHOW ALL COUNTRIES'}
          </Button>
        </Box>
      )}
    </Box>
  );
};
