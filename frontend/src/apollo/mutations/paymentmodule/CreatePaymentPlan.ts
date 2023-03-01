import { gql } from 'apollo-boost';

export const CREATE_PAYMENT_PLAN = gql`
  mutation CreatePP($input: CreatePaymentPlanInput!) {
    createPaymentPlan(input: $input) {
      paymentPlan {
        id
      }
    }
  }
`;
