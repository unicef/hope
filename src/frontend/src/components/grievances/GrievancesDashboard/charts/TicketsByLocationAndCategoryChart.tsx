import { Box, Button } from '@mui/material';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { FC, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import { formatThousands } from '@utils/utils';
import { DetailedChartData } from '@restgenerated/models/DetailedChartData';
import { categoriesAndColors } from '@components/grievances/utils/createGrievanceUtils';

interface TicketsByLocationAndCategoryChartProps {
  data: DetailedChartData;
}

export const TicketsByLocationAndCategoryChart: FC<
  TicketsByLocationAndCategoryChartProps
> = ({ data }) => {
  const lessDataCount = 5;
  const [showAll, setShowAll] = useState(false);
  const { t } = useTranslation();

  if (!data) return null;

  const matchDataSize = (
    dataToSlice: number[] | string[],
  ): number[] | string[] =>
    showAll ? dataToSlice : dataToSlice.slice(0, lessDataCount);

  const mappedDatasets = data.datasets.map((dataset) => {
    const color = categoriesAndColors.find(
      (c) => c.category.toLowerCase() === dataset.label.toLowerCase(),
    )?.color;
    return {
      ...dataset,
      categoryPercentage: 0.5,
      backgroundColor: color || '#000',
      data: matchDataSize(dataset.data).map((item) => item || ''),
      stack: 2,
      maxBarThickness: 15,
    };
  });

  const chartData: any = {
    labels: matchDataSize(data.labels),
    datasets: mappedDatasets,
  };

  const options: any = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      datalabels: {
        anchor: 'start',
        align: 'left',
        offset: 4,
        color: '#FFF',
        font: {
          weight: 'bold',
        },
        formatter: formatThousands,
      },
    },
    legend: {
      labels: {
        padding: 40,
      },
    },
    scales: {
      x: {
        display: true,
        position: 'top',
        ticks: {
          beginAtZero: true,
          stepSize: 1,
          callback: formatThousands,
        },
      },
      y: {
        position: 'left',
        grid: {
          display: false,
        },
      },
    },
  };

  const visibleRowCount = matchDataSize(data.labels).length;
  const chartHeight = Math.max(400, visibleRowCount * 45 + 80);

  return (
    <Box
      sx={{
        flexDirection: 'column',
      }}
    >
      <div style={{ height: `${chartHeight}px` }}>
        <Bar data={chartData} options={options} plugins={[ChartDataLabels]} />
      </div>
      {data.labels.length > lessDataCount ? (
        <Box
          sx={{
            textAlign: 'center',
            mt: 4,
            ml: 2,
            mr: 2,
            letterSpacing: 1.75,
          }}
        >
          <Button
            variant="outlined"
            color="primary"
            onClick={() => setShowAll(!showAll)}
            fullWidth
          >
            {showAll ? t('HIDE') : t('SHOW MORE LOCATIONS')}
          </Button>
        </Box>
      ) : null}
    </Box>
  );
};
