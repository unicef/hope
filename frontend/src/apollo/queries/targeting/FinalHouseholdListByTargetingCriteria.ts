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
    $excludedIds: String!
    $businessArea: String
  ) {
    finalHouseholdsListByTargetingCriteria(
      targetPopulation: $targetPopulation
      targetingCriteria: $targetingCriteria
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      excludedIds: $excludedIds
      businessArea: $businessArea
    ) {
      edges {
        node {
          id
          unicefId
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
          selection {
            vulnerabilityScore
          }
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
