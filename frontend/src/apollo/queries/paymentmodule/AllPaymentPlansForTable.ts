import { gql } from 'apollo-boost';

export const AllPaymentPlansForTable = gql`
  query AllPaymentPlansForTable(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $businessArea: String!
    $search: String
    $status: [String]
    $totalEntitledQuantityFrom: String
    $totalEntitledQuantityTo: String
    $dispersionStartDate: Date
    $dispersionEndDate: Date
  ) {
    allPaymentPlans(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      businessArea: $businessArea
      search: $search
      status: $status
      totalEntitledQuantityFrom: $totalEntitledQuantityFrom
      totalEntitledQuantityTo: $totalEntitledQuantityTo
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
          id
          unicefId
          status
          createdBy {
            id
            firstName
            lastName
            email
          }
          program {
            id
            name
          }
          targetPopulation {
            id
            name
          }
          currency
          currencyName
          startDate
          endDate
          dispersionStartDate
          dispersionEndDate
          femaleChildrenCount
          femaleAdultsCount
          maleChildrenCount
          maleAdultsCount
          totalHouseholdsCount
          totalIndividualsCount
          totalEntitledQuantity
          totalDeliveredQuantity
          totalUndeliveredQuantity
        }
      }
    }
  }
`;
