import { Box, Button } from '@mui/material';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { Bar } from 'react-chartjs-2';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  formatCurrencyWithSymbol,
  formatThousands,
  getPercentage,
} from '@utils/utils';
import { GlobalAreaChartsQuery } from '@generated/graphql';

interface TotalAmountTransferredByCountryChartProps {
  data: GlobalAreaChartsQuery['chartTotalTransferredCashByCountry'];
}

export function TotalAmountTransferredByCountryChart({
  data,
}: TotalAmountTransferredByCountryChartProps): React.ReactElement {
  const lessDataCount = 5;
  const [showAll, setShowAll] = useState(false);
  const { t } = useTranslation();

  if (!data) return null;

  const matchDataSize = (
    dataToSlice: string[] | number[],
  ): string[] | number[] =>
    showAll ? dataToSlice : dataToSlice.slice(0, lessDataCount);

  const chartData = {
    labels: matchDataSize(data.labels) as string[],
    datasets: [
      {
        categoryPercentage: 0.5,
        label: data.datasets[0].label,
        backgroundColor: '#03867B',
        data: matchDataSize(data.datasets[0].data) as number[],
        grouped: true,
        maxBarThickness: 15,
      },
      {
        categoryPercentage: 0.5,
        label: data.datasets[1].label,
        backgroundColor: '#FFAA1D',
        data: matchDataSize(data.datasets[1].data) as number[],
        grouped: true,
        maxBarThickness: 15,
      },
    ],
  };

  const options = {
    scales: {
      x: {
        title: {
          display: true,
          text: 'USD',
        },
        position: 'top',
        ticks: {
          callback: formatThousands,
        },
        min: 0,
        max: Math.max(...data.datasets[2].data) + 20000,
      },
      y: {
        position: 'left',
        grid: {
          display: false,
        },
      },
    },
    plugins: {
      datalabels: {
        align: 'end',
        anchor: 'end',
        formatter: (_, { datasetIndex, dataIndex }) => {
          if (datasetIndex === 1) {
            return formatCurrencyWithSymbol(data.datasets[2].data[dataIndex]);
          }
          return null;
        },
      },
      legend: {
        labels: {
          padding: 40,
        },
      },
      tooltip: {
        mode: 'nearest',
        callbacks: {
          label: (context) => {
            const tooltipData = context.chart.data;
            return ` ${
              tooltipData.datasets[context.datasetIndex].label
            }: ${formatCurrencyWithSymbol(context.parsed.x)} (${getPercentage(
              context.parsed.x,
              data.datasets[2].data[context.dataIndex],
            )})`;
          },
        },
      },
    },
  } as any;

  return (
    <Box flexDirection="column">
      <Bar data={chartData} options={options} plugins={[ChartDataLabels]} />
      {data.labels.length > lessDataCount ? (
        <Box textAlign="center" mt={4} ml={2} mr={2} letterSpacing={1.75}>
          <Button
            variant="outlined"
            color="primary"
            onClick={() => setShowAll(!showAll)}
            fullWidth
          >
            {showAll ? t('HIDE') : t('SHOW ALL COUNTRIES')}
          </Button>
        </Box>
      ) : null}
    </Box>
  );
}
