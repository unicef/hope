import { gql } from '@apollo/client';

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
    $documentType: String
    $documentNumber: String
    $residenceStatus: String
    $lastRegistrationDate: String
    $admin1: ID
    $admin2: ID
    $withdrawn: Boolean
    $headOfHouseholdPhoneNoValid: Boolean
    $program: ID
    $isActiveProgram: Boolean
    $rdiId: String
    $rdiMergeStatus: String
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
      documentType: $documentType
      documentNumber: $documentNumber
      residenceStatus: $residenceStatus
      lastRegistrationDate: $lastRegistrationDate
      admin1: $admin1
      admin2: $admin2
      withdrawn: $withdrawn
      headOfHousehold_PhoneNoValid: $headOfHouseholdPhoneNoValid
      program: $program
      isActiveProgram: $isActiveProgram
      rdiId: $rdiId
      rdiMergeStatus: $rdiMergeStatus
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
          program {
            id
            name
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
