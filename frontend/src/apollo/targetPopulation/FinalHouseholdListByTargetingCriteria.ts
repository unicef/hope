import { gql } from 'apollo-boost';

export const FinalHouseholdsListByTargetingCriteria = gql`
  query FinalHouseholdsListByTargetingCriteria(
    $targetPopulation: ID!
    $targetingCriteria: TargetingCriteriaObjectType
    $first: Int
    $after: String
    $before: String
    $last: Int
  ) {
    finalHouseholdsListByTargetingCriteria(
      targetPopulation: $targetPopulation
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
            givenName
            familyName
          }
          size
          adminArea{
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
