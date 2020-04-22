import { gql } from 'apollo-boost';

export const FinalHouseholdsListByTargetingCriteria = gql`
  query FinalHouseholdsListByTargetingCriteria(
    $id: ID!
    $targetingCriteria: TargetingCriteriaObjectType!
    $first: Int
    $after: String
    $before: String
    $last: Int
  ) {
    finalHouseholdsListByTargetingCriteria(
      targetPopulation: $id
      targetingCriteria: $targetingCriteria
      after: $after
      before: $before
      first: $first
      last: $last
    ) {
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
