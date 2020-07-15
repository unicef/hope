import { gql } from 'apollo-boost';

export const AllCashPlans = gql`
  query AllCashPlans(
    $program: ID
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $search: String
    $assistanceThrough: String
    $deliveryType: String
    $verificationStatus: String
  ) {
    allCashPlans(
      program: $program
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      search: $search
      assistanceThrough: $assistanceThrough
      deliveryType: $deliveryType
      verificationStatus: $verificationStatus
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
          caId
          verificationStatus
          assistanceThrough
          deliveryType
          startDate
          endDate
          program {
            id
            name
          }
          totalPersonsCovered
          dispersionDate
          assistanceMeasurement
          status
          totalEntitledQuantity
          totalDeliveredQuantity
          totalUndeliveredQuantity
          assistanceMeasurement
        }
      }
    }
  }
`;
