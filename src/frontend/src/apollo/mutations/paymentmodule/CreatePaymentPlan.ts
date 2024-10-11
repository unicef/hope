import { gql } from '@apollo/client';

export const CREATE_PAYMENT_PLAN = gql`
  mutation CreatePP($input: CreatePaymentPlanInput!) {
    createPaymentPlan(input: $input) {
      paymentPlan {
        id
      }
    }
  }
`;
