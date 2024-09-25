import { AllGrievanceDashboardChartsQuery } from '../../../src/__generated__/graphql';

export const fakeChartTicketsByLocationAndCategory = {
  datasets: [
    { data: [0, 0], label: 'Data Change', __typename: '_DetailedDatasetsNode' },
    {
      data: [0, 1],
      label: 'Grievance Complaint',
      __typename: '_DetailedDatasetsNode',
    },
    {
      data: [10, 0],
      label: 'Needs Adjudication',
      __typename: '_DetailedDatasetsNode',
    },
    {
      data: [0, 1],
      label: 'Negative Feedback',
      __typename: '_DetailedDatasetsNode',
    },
    {
      data: [0, 0],
      label: 'Payment Verification',
      __typename: '_DetailedDatasetsNode',
    },
    {
      data: [0, 1],
      label: 'Positive Feedback',
      __typename: '_DetailedDatasetsNode',
    },
    { data: [0, 7], label: 'Referral', __typename: '_DetailedDatasetsNode' },
    {
      data: [0, 0],
      label: 'Sensitive Grievance',
      __typename: '_DetailedDatasetsNode',
    },
    {
      data: [0, 0],
      label: 'System Flagging',
      __typename: '_DetailedDatasetsNode',
    },
  ],
  labels: ['Abband', 'Colombo'],
  __typename: 'ChartDetailedDatasetsNode',
} as AllGrievanceDashboardChartsQuery['ticketsByLocationAndCategory'];
