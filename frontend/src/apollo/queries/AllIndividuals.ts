import { gql } from 'apollo-boost';

export const AllIndividuals = gql`
  query AllIndividuals(
    $before: String
    $after: String
    $first: Int
    $last: Int
  ) {
    allIndividuals(before: $before, after: $after, first: $first, last: $last) {
      totalCount
      pageInfo {
        startCursor
        endCursor
      }
      edges {
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
