import { gql } from 'apollo-boost';

export const DashboardReportChoiceData = gql`
  query DashboardReportChoiceData($businessArea: String!) {
    dashboardReportTypesChoices(businessAreaSlug: $businessArea) {
      name
      value
    }
  }
`;
