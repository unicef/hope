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
  ) {
    allPaymentVerifications(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      cashPlanPaymentVerification: $cashPlanPaymentVerification
      search: $search
      status: $status
      businessArea: $businessArea
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
          paymentRecord {
            id
            caId
            deliveredQuantity
            currency
            household {
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
