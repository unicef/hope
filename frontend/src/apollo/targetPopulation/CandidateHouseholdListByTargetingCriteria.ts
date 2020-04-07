import { gql } from 'apollo-boost';

export const CandidateHouseholdsListByTargetingCriteria = gql`
  query candidateHouseholdsListByTargetingCriteria($targetPopulation: ID! $first: Int) {
    candidateHouseholdsListByTargetingCriteria(targetPopulation: $targetPopulation first: $first) {
      edges {
        node {
          id
          headOfHousehold {
            firstName
            lastName
          }
          familySize
          location {
            title
          }
          updatedAt
        }
      }
      totalCount
      edgeCount
    }
  }
`;
