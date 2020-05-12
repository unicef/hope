import { gql } from 'apollo-boost';

export const AllIndividuals = gql`
  query AllIndividuals(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $fullNameContains: String
    $sex: [ID]
    $age: String
    $orderBy: String
    $search: String
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
