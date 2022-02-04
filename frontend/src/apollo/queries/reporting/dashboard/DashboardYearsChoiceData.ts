import { gql } from 'apollo-boost';

export const DashboardYearsChoiceData = gql`
  query DashboardYearsChoiceData($businessArea: String!) {
    dashboardYearsChoices(businessAreaSlug: $businessArea)
  }
`;
