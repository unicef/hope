import { gql } from '@apollo/client';

export const DashboardReportChoiceData = gql`
  query DashboardReportChoiceData($businessArea: String!) {
    dashboardReportTypesChoices(businessAreaSlug: $businessArea) {
      name
      value
    }
  }
`;
