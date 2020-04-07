import { gql } from 'apollo-boost';

export const GoldenRecordByTargetingCriteria = gql`
  query GoldenRecordByTargetingCriteria($targetingCriteria:TargetingCriteriaObjectType! $first: Int) {
    goldenRecordByTargetingCriteria(targetingCriteria: $targetingCriteria first: $first) {
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
