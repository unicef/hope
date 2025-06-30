import { gql } from '@apollo/client';

export const BusinessAreaData = gql`
  query BusinessAreaData($businessAreaSlug: String!) {
    businessArea(businessAreaSlug: $businessAreaSlug) {
      id
      isAccountabilityApplicable
    }
  }
`;
