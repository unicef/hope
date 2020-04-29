import { gql } from 'apollo-boost';

export const CandidateHouseholdsListByTargetingCriteria = gql`
  query candidateHouseholdsListByTargetingCriteria(
    $targetPopulation: ID!
    $first: Int
    $after: String
    $before: String
    $last: Int
  ) {
    candidateHouseholdsListByTargetingCriteria(
      targetPopulation: $targetPopulation
      after: $after
      before: $before
      first: $first
      last: $last
    ) {
      edges {
        node {
          id
          headOfHousehold {
            id
            givenName
            familyName
          }
          size
          adminArea {
            id
            title
          }
          updatedAt
          address
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
