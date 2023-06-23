import { gql } from 'apollo-boost';

export const AllTargetPopulationForChoices = gql`
  query AllTargetPopulationForChoices(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $name: String
    $status: String
    $numberOfHouseholdsMin: Int
    $numberOfHouseholdsMax: Int
    $businessArea: String
    $program: [ID]
  ) {
    allTargetPopulation(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      name: $name
      status: $status
      totalHouseholdsCountMin: $numberOfHouseholdsMin
      totalHouseholdsCountMax: $numberOfHouseholdsMax
      businessArea: $businessArea
      program: $program
    ) {
      edges {
        node {
          id
          name
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
