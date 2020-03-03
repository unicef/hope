import { gql } from 'apollo-boost';

export const AllIndividuals = gql`
  query AllIndividuals(
    $before: String
    $after: String
    $first: Int
    $last: Int
    $fullName_Icontains: String
  ) {
    allIndividuals(
      before: $before
      after: $after
      first: $first
      last: $last
      fullName_Icontains: $fullName_Icontains
    ) {
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
