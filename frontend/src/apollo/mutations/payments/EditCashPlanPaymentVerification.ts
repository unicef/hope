import { gql } from 'apollo-boost';

export const EDIT_CASH_PLAN_PAYMENT_VERIFICATION_MUTATION = gql`
  mutation editCashPlanPaymentVerification(
    $input: EditCashPlanPaymentVerificationInput!
  ) {
    editCashPlanPaymentVerification(input: $input) {
      cashPlan {
        id
      }
    }
  }
`;
