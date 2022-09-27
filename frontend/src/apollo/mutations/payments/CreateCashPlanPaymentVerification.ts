import { gql } from 'apollo-boost';

export const CREATE_PAYMENT_VERIFICATION_MUTATION = gql`
  mutation createPaymentVerification(
    $input: CreateUpdatePaymentVerificationInput!
  ) {
    createPaymentVerification(input: $input) {
      paymentPlan {
        paymentVerificationSummary {
          id
        }
      }
    }
  }
`;
