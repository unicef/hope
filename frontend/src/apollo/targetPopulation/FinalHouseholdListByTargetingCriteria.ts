import { gql } from 'apollo-boost';

export const FinalHouseholdsListByTargetingCriteria = gql`
  query FinalHouseholdsListByTargetingCriteria(
    $targetPopulation: ID!
    $targetingCriteria: TargetingCriteriaObjectType
    $first: Int
    $after: String
    $before: String
    $last: Int
    $orderBy: String
  ) {
    finalHouseholdsListByTargetingCriteria(
      targetPopulation: $targetPopulation
      targetingCriteria: $targetingCriteria
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
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
