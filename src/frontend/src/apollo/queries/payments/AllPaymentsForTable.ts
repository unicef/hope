import { gql } from '@apollo/client';

export const AllPaymentsForTable = gql`
  query AllPaymentsForTable(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $businessArea: String!
    $paymentPlanId: String
    $householdId: String
  ) {
    allPayments(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      businessArea: $businessArea
      paymentPlanId: $paymentPlanId
      householdId: $householdId
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
          status
          vulnerabilityScore
          parent {
            program {
              id
              name
            }
          }
          household {
            id
            unicefId
            size
            admin2 {
              id
              name
            }
            headOfHousehold {
              id
              unicefId
              fullName
            }
            individuals {
              edges {
                node {
                  id
                  unicefId
                  fullName
                }
              }
            }
          }
          entitlementQuantity
          entitlementQuantityUsd
          currency
          deliveredQuantity
          deliveredQuantityUsd
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
            unicefId
            fullName
          }
          financialServiceProvider {
            id
            name
          }
          fspAuthCode
        }
      }
    }
  }
`;
