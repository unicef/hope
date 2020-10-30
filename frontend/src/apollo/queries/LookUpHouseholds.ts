import { gql } from 'apollo-boost';

export const LookUpHouseholds = gql`
  query LookUpHouseholds(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $businessArea: String
    $orderBy: String
    $familySize: String
    $programs: [ID]
    $headOfHouseholdFullNameIcontains: String
    $adminArea: ID
    $search: String
    $residenceStatus: String
  ) {
    allHouseholds(
      after: $after
      before: $before
      first: $first
      last: $last
      businessArea: $businessArea
      size: $familySize
      orderBy: $orderBy
      programs: $programs
      headOfHousehold_FullName_Icontains: $headOfHouseholdFullNameIcontains
      adminArea: $adminArea
      search: $search
      residenceStatus: $residenceStatus
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
          headOfHousehold {
            id
            fullName
          }
          size
          programs {
            edges {
              node {
                id
                name
              }
            }
          }
          firstRegistrationDate
          lastRegistrationDate
        }
      }
    }
  }
`;
