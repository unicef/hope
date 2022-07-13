import { Box, Button } from '@material-ui/core';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import React, { useState } from 'react';
import { HorizontalBar } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import {
  formatCurrencyWithSymbol,
  formatThousands,
  getPercentage,
} from '../../../../utils/utils';
import { AllGrievanceDashboardChartsQuery } from '../../../../__generated__/graphql';

interface TicketsByLocationAndCategoryChartProps {
  data: AllGrievanceDashboardChartsQuery['ticketsByLocationAndCategory'];
}

export const TicketsByLocationAndCategoryChart = ({
  data,
}: TicketsByLocationAndCategoryChartProps): React.ReactElement => {
  const lessDataCount = 5;
  const [showAll, setShowAll] = useState(false);
  const { t } = useTranslation();
  if (!data) return null;

  const matchDataSize = (
    dataToSlice: number[] | string[],
  ): number[] | string[] => {
    return showAll ? dataToSlice : dataToSlice.slice(0, lessDataCount);
  };

  // const mappedDatasets = data.map((el) => ({
  //   categoryPercentage: 0.5,
  //   label: el.location,
  //   backgroundColor: '#03867B',
  //   data: matchDataSize(data.datasets[0].data),
  //   stack: 2,
  //   maxBarThickness: 15,
  // }));

  // const chartData = {
  //   labels: matchDataSize(data.labels),
  //   datasets: mappedDatasets,
  // };

  // const options = {
  //   legend: {
  //     labels: {
  //       padding: 40,
  //     },
  //   },
  //   scales: {
  //     xAxes: [
  //       {
  //         scaleLabel: {
  //           display: false,
  //         },
  //         position: 'top',
  //         ticks: {
  //           beginAtZero: true,
  //           callback: formatThousands,
  //         },
  //       },
  //     ],
  //     yAxes: [
  //       {
  //         position: 'left',
  //         gridLines: {
  //           display: false,
  //         },
  //       },
  //     ],
  //   },
  // };

  return (
    <Box flexDirection='column'>
      {/* <HorizontalBar
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
            {showAll ? t('HIDE') : t('SHOW MORE LOCATIONS')}
          </Button>
        </Box>
      ) : null} */}
    </Box>
  );
};
