import { AllGrievanceDashboardChartsQuery } from '../../../src/__generated__/graphql';

export const fakeChartTicketsByCategory = {
  datasets: [{ data: [10, 7, 1, 1, 1], __typename: '_DatasetsNode' }],
  labels: [
    'Needs Adjudication',
    'Referral',
    'Grievance Complaint',
    'Negative Feedback',
    'Positive Feedback',
  ],
  __typename: 'ChartDatasetNode',
} as AllGrievanceDashboardChartsQuery['ticketsByCategory'];
