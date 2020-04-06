import { gql } from 'apollo-boost';

export const CandidateHouseholdsListByTargetingCriteria = gql`
  query candidateHouseholdsListByTargetingCriteria($targetPopulation: ID!) {
    candidateHouseholdsListByTargetingCriteria(targetPopulation: $targetPopulation) {
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
    }
  }
`;
