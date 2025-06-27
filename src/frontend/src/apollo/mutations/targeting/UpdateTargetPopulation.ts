import { gql } from '@apollo/client';

export const UpdateTP = gql`
  mutation UpdateTP($input: UpdatePaymentPlanInput!) {
    updatePaymentPlan(input: $input) {
      paymentPlan {
        id
        status
        totalHouseholdsCount
        totalIndividualsCount
      }
    }
  }
`;
