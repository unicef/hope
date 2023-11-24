import { gql } from 'apollo-boost';

export const AllHouseholdsForPopulationTable = gql`
  query AllHouseholdsForPopulationTable(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $businessArea: String
    $orderBy: String
    $familySize: String
    $headOfHouseholdFullNameIcontains: String
    $adminArea: ID
    $search: String
    $searchType: String
    $residenceStatus: String
    $lastRegistrationDate: String
    $admin2: ID
    $withdrawn: Boolean
    $headOfHouseholdPhoneNoValid: Boolean
    $program: ID
  ) {
    allHouseholds(
      after: $after
      before: $before
      first: $first
      last: $last
      businessArea: $businessArea
      size: $familySize
      orderBy: $orderBy
      headOfHousehold_FullName_Startswith: $headOfHouseholdFullNameIcontains
      adminArea: $adminArea
      search: $search
      searchType: $searchType
      residenceStatus: $residenceStatus
      lastRegistrationDate: $lastRegistrationDate
      admin2: $admin2
      withdrawn: $withdrawn
      headOfHousehold_PhoneNoValid: $headOfHouseholdPhoneNoValid
      program: $program
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
          status
          unicefId
          hasDuplicates
          sanctionListPossibleMatch
          sanctionListConfirmedMatch
          headOfHousehold {
            id
            fullName
          }
          size
          admin2 {
            id
            name
          }
          residenceStatus
          totalCashReceived
          currency
          lastRegistrationDate
          programs {
            edges {
              node {
                id
                name
              }
            }
          }
          program {
            id
            name
          }
        }
      }
    }
  }
`;
