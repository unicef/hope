import { gql } from '@apollo/client';

export const AllIndividualsForPopulationTable = gql`
  query AllIndividualsForPopulationTable(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $fullNameContains: String
    $sex: [String]
    $age: String
    $orderBy: String
    $search: String
    $documentType: String
    $documentNumber: String
    $programs: [ID]
    $status: [String]
    $lastRegistrationDate: String
    $householdId: UUID
    $excludedId: String
    $businessArea: String
    $adminArea: ID
    $withdrawn: Boolean
    $admin1: [ID]
    $admin2: [ID]
    $flags: [String]
    $program: ID
    $isActiveProgram: Boolean
  ) {
    allIndividuals(
      before: $before
      after: $after
      first: $first
      last: $last
      fullName_Startswith: $fullNameContains
      sex: $sex
      age: $age
      orderBy: $orderBy
      search: $search
      documentType: $documentType
      documentNumber: $documentNumber
      programs: $programs
      status: $status
      lastRegistrationDate: $lastRegistrationDate
      household_Id: $householdId
      excludedId: $excludedId
      businessArea: $businessArea
      household_AdminArea: $adminArea
      withdrawn: $withdrawn
      admin1: $admin1
      admin2: $admin2
      flags: $flags
      program: $program
      isActiveProgram: $isActiveProgram
    ) {
      totalCount
      pageInfo {
        startCursor
        endCursor
      }
      edges {
        cursor
        node {
          id
          unicefId
          sanctionListPossibleMatch
          sanctionListConfirmedMatch
          deduplicationGoldenRecordStatus
          status
          sanctionListLastCheck
          fullName
          household {
            id
            unicefId
            admin2 {
              id
              name
            }
          }
          relationship
          age
          sex
          lastRegistrationDate
          program {
            id
            name
          }
        }
      }
    }
  }
`;
