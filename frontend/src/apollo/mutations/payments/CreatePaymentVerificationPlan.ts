import { gql } from 'apollo-boost';

export const CREATE_PAYMENT_VERIFICATION_MUTATION = gql`
mutation CreatePaymentVerificationPlan($input: CreatePaymentVerificationInput!) {
  createPaymentVerificationPlan(input: $input) {
    paymentPlan {
      id
      # paymentVerificationSummary {
      #   id
      #   status
      # }
    }
  }
}
`;
