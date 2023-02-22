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
    $businessArea: String!
    $verificationChannel: String
    $paymentPlanId: String
  ) {
    allPaymentVerifications(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      paymentVerificationPlan: $paymentVerificationPlan
      search: $search
      status: $status
      businessArea: $businessArea
      verificationChannel: $verificationChannel
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
          paymentVerificationPlan {
            id
            unicefId
            verificationChannel
          }
          payment {
            id
            unicefId
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
