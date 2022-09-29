import { gql } from 'apollo-boost';

export const EDIT_CASH_PLAN_PAYMENT_VERIFICATION_MUTATION = gql`
  mutation editPaymentVerificationPlan(
    $input: CreateUpdatePaymentVerificationInput!
  ) {
    editPaymentVerification(input: $input) {
      paymentPlan {
        paymentVerificationSummary {
          id
        }
      }
    }
  }
`;
