import { gql } from 'apollo-boost';

export const AllPaymentVerifications = gql`
  query AllPaymentVerifications(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $cashPlanPaymentVerification: ID
    $search: String
    $status: String
    $businessArea: String
    $cashPlanId: ID
    $verificationChannel: String
  ) {
    allPaymentVerifications(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      cashPlanPaymentVerification: $cashPlanPaymentVerification
      cashPlanPaymentVerification_CashPlan: $cashPlanId
      search: $search
      status: $status
      businessArea: $businessArea
      verificationChannel: $verificationChannel
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
          cashPlanPaymentVerification {
            id
            unicefId
            verificationChannel
          }
          paymentRecord {
            id
            caId
            deliveredQuantity
            currency
            household {
              status
              unicefId
              id
              headOfHousehold {
                id
                fullName
                phoneNo
                phoneNoAlternative
              }
            }
          }
          status
          receivedAmount
        }
      }
    }
  }
`;
