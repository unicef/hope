import { gql } from 'apollo-boost';

export const TargetPopulationHouseholds = gql`
  query TargetPopulationHouseholds(
    $targetPopulation: ID!
    $first: Int
    $after: String
    $before: String
    $last: Int
    $orderBy: String
    $businessArea: String
  ) {
    targetPopulationHouseholds(
      targetPopulation: $targetPopulation
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
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
            fullName
          }
          size
          adminArea {
            id
            name
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
