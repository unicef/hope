import React from 'react';
import { Bar } from 'react-chartjs-2';
import * as ChartAnnotation from 'chartjs-plugin-annotation';
import { AllChartsQuery } from '../../../__generated__/graphql';

interface PlannedBudgetProps {
  data: AllChartsQuery['chartPlannedBudget'];
}
export const PlannedBudget = ({
  data,
}: PlannedBudgetProps): React.ReactElement => {
  const chartdata = {
    labels: data.labels,
    datasets: [
      {
        barPercentage: 0.4,
        label: data?.datasets[0]?.label,
        backgroundColor: '#C3D1D8',
        data: data?.datasets[0]?.data,
      },
      {
        barPercentage: 0.4,
        label: data?.datasets[1]?.label,
        backgroundColor: '#FFAA1D',
        data: data?.datasets[1]?.data,
      },
      // {
      //   barPercentage: 0.4,
      //   label: data?.datasets[2]?.label,
      //   backgroundColor: '#03867B',
      //   data: data?.datasets[2]?.data,
      // },
    ],
  };

  const options = {
    barPercentage: 0.1,
    legend: {
      position: 'bottom',
    },
    scales: {
      xAxes: [
        {
          stacked: true,
        },
      ],
      yAxes: [
        {
          scaleLabel: {
            display: true,
            labelString: 'USD',
          },
          stacked: true,
          position: 'right',
        },
      ],
    },
    // annotation: {
    //   annotations: [
    //     {
    //       drawTime: 'afterDatasetsDraw',
    //       id: 'hline',
    //       type: 'line',
    //       mode: 'horizontal',
    //       scaleID: 'y-axis-0',
    //       value: 1500000,
    //       borderColor: '#5A5A5A',
    //       borderWidth: 4,
    //     },
    //   ],
    // },
  };

  return <Bar data={chartdata} options={options} plugins={ChartAnnotation} />;
};
