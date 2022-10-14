import { gql } from 'apollo-boost';

export const AllTargetPopulations = gql`
  query AllTargetPopulations(
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
    $createdAtRange: String
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
      createdAtRange: $createdAtRange
    ) {
      edges {
        node {
          ...targetPopulationMinimal
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
