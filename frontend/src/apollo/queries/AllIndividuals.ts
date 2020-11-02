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
    $programme: String
    $status: [String]
    $lastRegistrationDate: String
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
      programme: $programme
      status: $status
      lastRegistrationDate: $lastRegistrationDate
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
