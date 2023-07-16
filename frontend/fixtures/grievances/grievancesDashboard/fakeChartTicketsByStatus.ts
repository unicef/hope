import { AllGrievanceDashboardChartsQuery } from '../../../src/__generated__/graphql';

export const fakeChartTicketsByStatus = {
  datasets: [{ data: [9, 8, 2, 1], __typename: '_DatasetsNode' }],
  labels: ['Assigned', 'New', 'For Approval', 'Closed'],
  __typename: 'ChartDatasetNode',
} as AllGrievanceDashboardChartsQuery['ticketsByStatus'];
