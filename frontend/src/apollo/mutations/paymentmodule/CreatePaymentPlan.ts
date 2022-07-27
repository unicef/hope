import { gql } from 'apollo-boost';

export const CREATE_PAYMENT_PLAN = gql`
  mutation CreatePaymentPlan(
    $businessAreaSlug: String!
    $targetingId: ID!
    $startDate: Date!
    $endDate: Date!
    $dispersionStartDate: Date!
    $dispersionEndDate: Date!
    $currency: String!
  ) {
    createPaymentPlan(
      businessAreaSlug: $businessAreaSlug
      targetingId: $targetingId
      startDate: $startDate
      endDate: $endDate
      dispersionStartDate: $dispersionStartDate
      dispersionEndDate: $dispersionEndDate
      currency: $currency
    ) {
      paymentPlan {
        id
      }
      validationErrors
    }
  }
`;
