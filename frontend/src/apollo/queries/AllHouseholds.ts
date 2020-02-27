import { gql } from 'apollo-boost';

export const AllHouseholds = gql`
  query AllHouseholds(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $businessArea: String
    $orderBy: String
  ) {
    allHouseholds(
      after: $after
      before: $before
      first: $first
      last: $last
      businessArea: $businessArea
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
          individuals {
            totalCount
          }
          paymentRecords {
            edges {
              node {
                id
                headOfHousehold
                cashPlan {
                  id
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
