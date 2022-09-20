import { gql } from 'apollo-boost';

export const AllPaymentVerifications = gql`
  query AllPaymentVerifications(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $paymentVerificationPlan: ID
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
      paymentVerificationPlan: $paymentVerificationPlan
      paymentVerificationPlan_CashPlan: $cashPlanId
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
          paymentVerificationPlan {
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
                familyName
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
