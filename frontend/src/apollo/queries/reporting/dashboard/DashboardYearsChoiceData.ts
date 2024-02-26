import { gql } from '@apollo/client';

export const DashboardYearsChoiceData = gql`
  query DashboardYearsChoiceData($businessArea: String!) {
    dashboardYearsChoices(businessAreaSlug: $businessArea)
  }
`;
