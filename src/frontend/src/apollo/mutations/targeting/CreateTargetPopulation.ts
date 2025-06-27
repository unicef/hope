import { gql } from '@apollo/client';

export const CreateTP = gql`
  mutation CreateTP($input: CreatePaymentPlanInput!) {
    createPaymentPlan(input: $input) {
      paymentPlan {
        id
        status
        totalHouseholdsCount
        totalIndividualsCount
      }
    }
  }
`;
