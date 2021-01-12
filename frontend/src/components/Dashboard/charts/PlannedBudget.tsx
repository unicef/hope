import React from 'react';
import { Bar } from 'react-chartjs-2';
import * as ChartAnnotation from 'chartjs-plugin-annotation';

export const PlannedBudget = (): React.ReactElement => {
  const data = {
    labels: [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ],
    datasets: [
      {
        barPercentage: 0.4,
        label: 'Previous Transfers',
        backgroundColor: '#C3D1D8',
        data: [
          10000,
          100000,
          120000,
          160000,
          180000,
          200000,
          210000,
          220000,
          240000,
          300000,
          310000,
          330000,
        ],
      },
      {
        barPercentage: 0.4,
        label: 'Voucher Assistance',
        backgroundColor: '#FFAA1D',
        data: [
          8000,
          90000,
          110000,
          140000,
          150000,
          190000,
          230000,
          270000,
          290000,
          330000,
          350000,
          370000,
        ],
      },
      {
        barPercentage: 0.4,
        label: 'Cash Assistance',
        backgroundColor: '#03867B',
        data: [
          3000,
          80000,
          100000,
          140000,
          150000,
          170000,
          190000,
          200000,
          210000,
          220000,
          240000,
          270000,
        ],
      },
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

  return <Bar data={data} options={options} plugins={ChartAnnotation} />;
};
