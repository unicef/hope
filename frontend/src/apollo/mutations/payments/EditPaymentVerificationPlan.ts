import { gql } from 'apollo-boost';

export const EDIT_CASH_PLAN_PAYMENT_VERIFICATION_MUTATION = gql`
mutation EditPaymentVerificationPlan($input: EditPaymentVerificationInput!) {
  editPaymentVerificationPlan(input: $input) {
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
