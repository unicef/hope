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
  $page: Int
  $pageSize: Int
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
    page: $page
    pageSize: $pageSize
  ) {
    page
    pages
    pageSize
    totalCount
    hasNext
    hasPrev
    objects {
      objType
      id
      unicefId
      verificationStatus
      fspNames
      deliveryMechanisms
      deliveryTypes
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
`;
