import { gql } from 'apollo-boost';

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
    $programs: [ID]
    $status: [String]
    $lastRegistrationDate: String
    $householdId: UUID
  ) {
    allIndividuals(
      before: $before
      after: $after
      first: $first
      last: $last
      fullName_Icontains: $fullNameContains
      sex: $sex
      age: $age
      orderBy: $orderBy
      search: $search
      programs: $programs
      status: $status
      lastRegistrationDate: $lastRegistrationDate
      household_Id: $householdId
    ) {
      totalCount
      pageInfo {
        startCursor
        endCursor
      }
      edges {
        cursor
        node {
          ...individualMinimal
        }
      }
    }
  }
`;
