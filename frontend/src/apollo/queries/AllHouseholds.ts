import { gql } from 'apollo-boost';

export const AllHouseholds = gql`
  query AllHouseholds(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $businessArea: String
    $familySizeGreater: Float
    $familySizeLower: Float
    $orderBy: String
  ) {
    allHouseholds(
      after: $after
      before: $before
      first: $first
      last: $last
      businessArea: $businessArea
      familySizeGreater: $familySizeGreater
      familySizeLower: $familySizeLower
      orderBy: $orderBy
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
          createdAt
          householdCaId
          residenceStatus
          familySize
          location {
            id
            title
          }
          paymentRecords {
            edges {
              node {
                id
                headOfHousehold
                cashPlan {
                  program {
                    id
                    name
                  }
                  totalDeliveredQuantity
                }
              }
            }
          }
        }
      }
    }
  }
`;
