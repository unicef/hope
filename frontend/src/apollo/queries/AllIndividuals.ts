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
          createdAt
          updatedAt
          individualCaId
          fullName
          sex
          dob
          nationality
          martialStatus
          phoneNumber
          identificationType
          identificationNumber
          household {
            id
            householdCaId
            location {
              id
              title
            }
          }
        }
      }
    }
  }
`;
