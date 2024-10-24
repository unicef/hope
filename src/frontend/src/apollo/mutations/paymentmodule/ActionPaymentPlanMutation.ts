import { gql } from '@apollo/client';

export const ACTION_PAYMENT_PLAN = gql`
  mutation ActionPP($input: ActionPaymentPlanInput!) {
    actionPaymentPlanMutation(input: $input) {
      paymentPlan {
        id
        status
      }
    }
  }
`;
