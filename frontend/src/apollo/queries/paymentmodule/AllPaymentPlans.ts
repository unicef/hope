import { gql } from 'apollo-boost';

export const PaymentPlans = gql`
  query AllPaymentPlans(
    $businessArea: String!
    $search: String
    $status: [String]
    $totalEntitledQuantity: String
    $dispersionStartDate: Date
    $dispersionEndDate: Date
  ) {
    allPaymentPlans(
      businessArea: $businessArea
      search: $search
      status: $status
      totalEntitledQuantity: $totalEntitledQuantity
      dispersionStartDate: $dispersionStartDate
      dispersionEndDate: $dispersionEndDate
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
          isRemoved
          unicefId
          id
          createdAt
          businessArea {
            id
            slug
            code
            name
            longName
          }
          statusDate
          startDate
          endDate
          program {
            isRemoved
            id
            createdAt
            updatedAt
            version
            name
            status
            startDate
            endDate
            description
            caId
            caHashId
            budget
          }
          exchangeRate
          totalEntitledQuantity
          totalEntitledQuantityUsd
          totalEntitledQuantityRevised
          totalEntitledQuantityRevisedUsd
          totalDeliveredQuantity
          totalDeliveredQuantityUsd
          totalUndeliveredQuantity
          totalUndeliveredQuantityUsd
          createdBy {
            id
            username
            firstName
            lastName
          }
          status
          targetPopulation {
            name
            id
          }
          currency
          dispersionStartDate
          dispersionEndDate
          femaleChildrenCount
          maleChildrenCount
          femaleAdultsCount
          maleAdultsCount
          totalHouseholdsCount
          totalIndividualsCount
        }
      }
    }
  }
`;
