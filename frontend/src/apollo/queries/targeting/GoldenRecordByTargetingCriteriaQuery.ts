import { gql } from 'apollo-boost';

export const GoldenRecordByTargetingCriteria = gql`
  query GoldenRecordByTargetingCriteria(
    $targetingCriteria: TargetingCriteriaObjectType!
    $first: Int
    $after: String
    $before: String
    $last: Int
    $orderBy: String
    $program: ID!
    $excludedIds: String!
    $businessArea: String
    $criteriaFitRange: Int[]
  ) {
    goldenRecordByTargetingCriteria(
      targetingCriteria: $targetingCriteria
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      program: $program
      excludedIds: $excludedIds
      businessArea: $businessArea
      criteriaFitRange: $criteriaFitRange
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
            name
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
