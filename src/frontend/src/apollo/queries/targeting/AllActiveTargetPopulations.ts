import { gql } from '@apollo/client';

export const AllActiveTargetPopulations = gql`
  query AllActiveTargetPopulations(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $name: String
    $status: String
    $totalHouseholdsCountWithValidPhoneNoMin: Int
    $totalHouseholdsCountWithValidPhoneNoMax: Int
    $totalHouseholdsCountMin: Int
    $totalHouseholdsCountMax: Int
    $businessArea: String
    $program: [ID]
    $createdAtRange: String
    $statusNot: String
  ) {
    allActiveTargetPopulations(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      name: $name
      status: $status
      totalHouseholdsCountWithValidPhoneNoMin: $totalHouseholdsCountWithValidPhoneNoMin
      totalHouseholdsCountWithValidPhoneNoMax: $totalHouseholdsCountWithValidPhoneNoMax
      totalHouseholdsCountMin: $totalHouseholdsCountMin
      totalHouseholdsCountMax: $totalHouseholdsCountMax
      businessArea: $businessArea
      program: $program
      createdAtRange: $createdAtRange
      statusNot: $statusNot
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
          totalHouseholdsCountWithValidPhoneNo
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
