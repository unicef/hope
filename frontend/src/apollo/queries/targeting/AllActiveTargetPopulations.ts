import { gql } from 'apollo-boost';

export const AllActiveTargetPopulations = gql`
  query AllActiveTargetPopulations(
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
    allActiveTargetPopulations(
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
          id
          name
          status
          program {
            id
            name
          }
          totalHouseholdsCount
          createdAt
          updatedAt
          createdBy {
            id
            email
            firstName
            lastName
          }
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
