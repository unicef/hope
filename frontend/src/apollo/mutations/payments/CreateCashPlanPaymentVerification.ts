import { gql } from 'apollo-boost';

export const CREATE_CASH_PLAN_PAYMENT_VERIFICATION_MUTATION = gql`
  mutation createCashPlanPaymentVerification(
    $input: CreatePaymentVerificationInput!
  ) {
    createCashPlanPaymentVerification(input: $input) {
      cashPlan {
        id
      }
    }
  }
`;
