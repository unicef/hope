import { gql } from 'apollo-boost';

export const EDIT_CASH_PLAN_PAYMENT_VERIFICATION_MUTATION = gql`
mutation EditPaymentVerificationPlan($input: CreateUpdatePaymentVerificationInput!) {
  editPaymentVerificationPlan(input: $input) {
    paymentPlan {
      paymentVerificationSummary {
        id
        status
      }
    }
  }
}
`;
