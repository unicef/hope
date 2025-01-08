import { gql } from '@apollo/client';

export const AllTargetPopulations = gql`
  query AllTargetPopulations(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $name: String
    $status: [String]
    $totalHouseholdsCountMin: Int
    $totalHouseholdsCountMax: Int
    $businessArea: String!
    $program: String
    $programCycle: String
    $createdAtRange: String
  ) {
    allPaymentPlans(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      name: $name
      status: $status
      totalHouseholdsCountMin: $totalHouseholdsCountMin
      totalHouseholdsCountMax: $totalHouseholdsCountMax
      businessArea: $businessArea
      program: $program
      programCycle: $programCycle
      createdAtRange: $createdAtRange
    ) {
      edges {
        cursor
        node {
          id
          unicefId
          name
          isFollowUp
          followUps {
            totalCount
            edges {
              node {
                id
                unicefId
                dispersionStartDate
                dispersionEndDate
              }
            }
          }
          status
          createdAt
          updatedAt
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
