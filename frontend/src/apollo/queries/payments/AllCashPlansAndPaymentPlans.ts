import { gql } from 'apollo-boost';

export const AllCashPlansAndPaymentPlans = gql`
query AllCashPlansAndPaymentPlans(
  $businessArea: String!
  $program: String
  $search: String
  $serviceProvider: String
  $deliveryType: String
  $verificationStatus: String
  $startDateGte: String
  $endDateLte: String
  $orderBy: String
  $first: Int
  $last: Int
  $before: String
  $after: String
) {
  allCashPlansAndPaymentPlans(
    businessArea: $businessArea
    program: $program
    search: $search
    serviceProvider: $serviceProvider
    deliveryType: $deliveryType
    verificationStatus: $verificationStatus
    startDateGte: $startDateGte
    endDateLte: $endDateLte
    orderBy: $orderBy
    first: $first
    last: $last
    before: $before
    after: $after
  ) {
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
    }
    totalCount
    edges {
      cursor
      node {
        objType
        id
        unicefId
        verificationStatus
        currency
        totalDeliveredQuantity
        startDate
        endDate
        programmeName
        updatedAt
        verificationPlans {
          id
          createdAt
          unicefId
        }
        totalNumberOfHouseholds
        assistanceMeasurement
        totalEntitledQuantity
        totalUndeliveredQuantity
        dispersionDate
        serviceProviderFullName
      }
    }
  }
}
`;
