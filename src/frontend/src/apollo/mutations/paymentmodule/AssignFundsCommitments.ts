import { gql } from '@apollo/client';

export const ASSIGN_FUNDS_COMMITMENTS = gql`
  mutation AssignFundsCommitmentsPaymentPlan(
    $paymentPlanId: ID!
    $fundCommitmentItemsIds: [String!]!
  ) {
    assignFundsCommitments(
      paymentPlanId: $paymentPlanId
      fundCommitmentItemsIds: $fundCommitmentItemsIds
    ) {
      paymentPlan {
        id
        availableFundsCommitments {
          fundsCommitmentNumber
          fundsCommitmentItems {
            paymentPlan {
              id
              name
            }
            fundsCommitmentItem
            recSerialNumber
          }
        }
      }
    }
  }
`;