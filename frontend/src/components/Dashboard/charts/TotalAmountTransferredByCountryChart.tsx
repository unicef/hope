import { Box, Button } from '@material-ui/core';
import React, { useState } from 'react';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { HorizontalBar } from 'react-chartjs-2';
import {
  formatCurrencyWithSymbol,
  formatThousands,
  getPercentage,
} from '../../../utils/utils';
import { GlobalAreaChartsQuery } from '../../../__generated__/graphql';
import { useTranslation } from 'react-i18next';

interface TotalAmountTransferredByCountryChartProps {
  data: GlobalAreaChartsQuery['chartTotalTransferredCashByCountry'];
}

export const TotalAmountTransferredByCountryChart = ({
  data,
}: TotalAmountTransferredByCountryChartProps): React.ReactElement => {
  const lessDataCount = 5;
  const [showAll, setShowAll] = useState(false);
  const { t } = useTranslation();

  if (!data) return null;

  const matchDataSize = (
    dataToSlice: number[] | string[],
  ): number[] | string[] => {
    return showAll ? dataToSlice : dataToSlice.slice(0, lessDataCount);
  };

  const chartData = {
    labels: matchDataSize(data.labels),
    datasets: [
      {
        categoryPercentage: 0.5,
        label: data.datasets[0].label,
        backgroundColor: '#03867B',
        data: matchDataSize(data.datasets[0].data),
        stack: 2,
        maxBarThickness: 15,
      },
      {
        categoryPercentage: 0.5,
        label: data.datasets[1].label,
        backgroundColor: '#FFAA1D',
        data: matchDataSize(data.datasets[1].data),
        stack: 2,
        maxBarThickness: 15,
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
          }: ${formatCurrencyWithSymbol(tooltipItem.xLabel)} (${getPercentage(
            tooltipItem.xLabel,
            data.datasets[2].data[tooltipItem.index],
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
            callback: formatThousands,
            // NOTE: this is added to make sure the label that goes next to the bar fits inside the canvas
            // however it might be good to see if there is a better more dynamic way to set this value
            suggestedMax: Math.max(...data.datasets[2].data) + 20000,
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
          if (datasetIndex === 1) {
            return formatCurrencyWithSymbol(data.datasets[2].data[dataIndex]);
          }
          return null;
        },
      },
    },
  };

  return (
    <Box flexDirection='column'>
      <HorizontalBar
        data={chartData}
        options={options}
        plugins={[ChartDataLabels]}
      />
      {data.labels.length > lessDataCount ? (
        <Box textAlign='center' mt={4} ml={2} mr={2} letterSpacing={1.75}>
          <Button
            variant='outlined'
            color='primary'
            onClick={() => setShowAll(!showAll)}
            fullWidth
          >
            {showAll ? t('HIDE') : t('SHOW ALL COUNTRIES')}
          </Button>
        </Box>
      ) : null}
    </Box>
  );
};
