import { gql } from '@apollo/client';

export const AllTargetPopulationForChoices = gql`
  query AllTargetPopulationForChoices(
    $after: String
    $before: String
    $first: Int
    $last: Int
    $orderBy: String
    $name: String
    $businessArea: String!
    $program: String!
    $status: [String]
  ) {
    allPaymentPlans(
      after: $after
      before: $before
      first: $first
      last: $last
      orderBy: $orderBy
      name: $name
      businessArea: $businessArea
      program: $program
      status: $status
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
