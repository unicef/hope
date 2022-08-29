import { gql } from 'apollo-boost';

export const AllPaymentsForTable = gql`
  query AllPaymentsForTable(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $businessArea: String!
    $paymentPlanId: String!
  ) {
    allPayments(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      businessArea: $businessArea
      paymentPlanId: $paymentPlanId
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
      edges {
        cursor
        node {
          id
          unicefId
          household {
            id
            unicefId
            size
            admin2 {
              id
              name
            }
          }
          entitlementQuantityUsd
          paymentPlanHardConflicted
          paymentPlanSoftConflicted
          paymentPlanHardConflictedData {
            paymentPlanUnicefId
            paymentPlanId
            paymentPlanStartDate
            paymentPlanEndDate
            paymentPlanStatus
            paymentId
            paymentUnicefId
          }
          paymentPlanSoftConflictedData {
            paymentPlanUnicefId
            paymentPlanId
            paymentPlanStartDate
            paymentPlanEndDate
            paymentPlanStatus
            paymentId
            paymentUnicefId
          }
          collector {
            id
            fullName
          }
          hasPaymentChannel
        }
      }
    }
  }
`;
