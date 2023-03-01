import { gql } from 'apollo-boost';

export const BusinessAreaData = gql`
  query BusinessAreaData($businessAreaSlug: String!) {
    businessArea(businessAreaSlug: $businessAreaSlug) {
      id
      screenBeneficiary
      isPaymentPlanApplicable
    }
  }
`;
