import { gql } from 'apollo-boost';

export const AllHouseholds = gql`
  query AllHouseholds(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $businessArea: String
    $orderBy: String
    $familySize: String
    $headOfHouseholdFullNameIcontains: String
  ) {
    allHouseholds(
      after: $after
      before: $before
      first: $first
      last: $last
      businessArea: $businessArea
      familySize: $familySize
      orderBy: $orderBy
      headOfHousehold_FullName_Icontains: $headOfHouseholdFullNameIcontains
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
          totalCashReceived
          registrationDate
          headOfHousehold {
            id
            fullName
          }
          location {
            id
            title
          }
          individuals {
            totalCount
          }
        }
      }
    }
  }
`;
