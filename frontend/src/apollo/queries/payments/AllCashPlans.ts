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
    $serviceProvider: String
    $deliveryType: [String]
    $verificationStatus: [String]
    $startDateGte: DateTime
    $endDateLte: DateTime
    $businessArea: String
  ) {
    allCashPlans(
      program: $program
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      search: $search
      serviceProvider_FullName_Startswith: $serviceProvider
      deliveryType: $deliveryType
      verificationStatus: $verificationStatus
      startDate_Gte: $startDateGte
      endDate_Lte: $endDateLte
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
          caId
          assistanceThrough
          totalNumberOfHouseholds
          serviceProvider {
            id
            caId
            fullName
          }
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
          currency
          totalEntitledQuantity
          totalDeliveredQuantity
          totalUndeliveredQuantity
          updatedAt
          paymentVerificationSummary {
            edges {
              node {
                id
                status
              }
            }
          }
        }
      }
    }
  }
`;
