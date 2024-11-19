import { gql } from '@apollo/client';

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
    $headOfHouseholdPhoneNoValid: Boolean
    $adminArea: ID
    $search: String
    $residenceStatus: String
    $lastRegistrationDate: String
    $admin2: ID
    $withdrawn: Boolean
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
      headOfHousehold_PhoneNoValid: $headOfHouseholdPhoneNoValid
      adminArea: $adminArea
      search: $search
      residenceStatus: $residenceStatus
      lastRegistrationDate: $lastRegistrationDate
      admin2: $admin2
      withdrawn: $withdrawn
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
            phoneNo
            birthDate
            phoneNo
            relationship
          }
          size
          address
          village
          maleChildrenCount
          femaleChildrenCount
          childrenDisabledCount
          admin1 {
            id
            name
          }
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
        }
      }
    }
  }
`;
