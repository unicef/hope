import { gql } from 'apollo-boost';

export const CREATE_PAYMENT_VERIFICATION_MUTATION = gql`
mutation CreatePaymentVerificationPlan($input: CreateUpdatePaymentVerificationInput!) {
  createPaymentVerificationPlan(input: $input) {
    paymentPlan {
      paymentVerificationSummary {
        id
      }
    }
  }
}
`;
