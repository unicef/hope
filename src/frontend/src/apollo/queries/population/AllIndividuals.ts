import { gql } from '@apollo/client';

export const AllIndividuals = gql`
  query AllIndividuals(
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
    $admin2: [ID]
    $flags: [String]
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
      admin2: $admin2
      flags: $flags
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
          sanctionListLastCheck
          fullName
          household {
            id
            unicefId
            admin2 {
              id
              name
            }
            programs {
              edges {
                node {
                  id
                  name
                }
              }
            }
          }
          relationship
          age
          sex
          lastRegistrationDate
          phoneNo
          birthDate
          documents {
            edges {
              node {
                id
                country
                countryIso3
                documentNumber
                photo
                type {
                  label
                  key
                }
              }
            }
          }
          identities {
            edges {
              node {
                id
                partner
                country
                countryIso3
                number
              }
            }
          }
          paymentChannels {
            id
            bankName
            bankAccountNumber
            accountHolderName
            bankBranchName
          }
        }
      }
    }
  }
`;
