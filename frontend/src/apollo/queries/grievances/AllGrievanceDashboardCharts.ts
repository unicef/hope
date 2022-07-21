import { gql } from 'apollo-boost';

export const AllGrievanceDashboardCharts = gql`
  query AllGrievanceDashboardCharts($businessAreaSlug: String!) {
    ticketsByType(businessAreaSlug: $businessAreaSlug) {
      userGeneratedCount
      systemGeneratedCount
      closedUserGeneratedCount
      closedSystemGeneratedCount
      userGeneratedAvgResolution
      systemGeneratedAvgResolution
    }
    ticketsByStatus(businessAreaSlug: $businessAreaSlug) {
      datasets {
        data
      }
      labels
    }
    ticketsByCategory(businessAreaSlug: $businessAreaSlug) {
      datasets {
        data
      }
      labels
    }

    ticketsByLocationAndCategory(businessAreaSlug: $businessAreaSlug) {
      datasets {
        data
        label
      }
      labels
    }
  }
`;
