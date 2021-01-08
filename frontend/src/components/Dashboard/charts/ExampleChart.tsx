import React from 'react';
import { Bar } from 'react-chartjs-2';

export const ExampleChart = (): React.ReactElement => {
  const data = {
    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
    datasets: [
      {
        type: 'line',
        label: 'Dataset 1',
        borderColor: 'blue',
        borderWidth: 2,
        fill: false,
        data: [2, 2, 5, 7, 8, 8, 9],
      },
      {
        type: 'bar',
        label: 'Dataset 2',
        backgroundColor: 'red',
        data: [3, 3, 5, 8, 7, 6, 5],
        borderColor: 'white',
        borderWidth: 2,
      },
      {
        type: 'bar',
        label: 'Dataset 3',
        backgroundColor: 'green',
        data: [2, 2, 4, 6, 7, 9, 9],
      },
    ],
  };
  const options = {
    responsive: true,
    title: {
      display: true,
      text: 'Chart.js Combo Bar Line Chart',
    },
    tooltips: {
      mode: 'index',
      intersect: true,
    },
    annotation: {
      events: ['click'],
      annotations: [
        {
          drawTime: 'afterDatasetsDraw',
          id: 'hline',
          type: 'line',
          mode: 'horizontal',
          scaleID: 'y-axis-0',
          value: 7,
          borderColor: 'black',
          borderWidth: 25,
          label: {
            backgroundColor: 'red',
            content: 'Test Label',
            enabled: true,
          },
          onClick: (e) => console.log('Annotation', e.type, this),
        },
        // {
        //   drawTime: 'beforeDatasetsDraw',
        //   type: 'box',
        //   xScaleID: 'x-axis-0',
        //   yScaleID: 'y-axis-0',
        //   xMin: 'February',
        //   xMax: 'April',
        //   yMin: 2,
        //   yMax: 10,
        //   backgroundColor: 'rgba(101, 33, 171, 0.5)',
        //   borderColor: 'rgb(101, 33, 171)',
        //   borderWidth: 1,
        //   onClick: (e) => console.log('Box', e.type, this),
        // },
      ],
    },
  };

  return <Bar data={data} options={options} />;
};
