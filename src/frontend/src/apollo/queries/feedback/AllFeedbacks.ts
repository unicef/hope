import { gql } from '@apollo/client';

export const AllFeedbacks = gql`
  query AllFeedbacks(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $issueType: String
    $createdAtRange: String
    $createdBy: String
    $feedbackId: String
    $orderBy: String
    $program: String
    $isActiveProgram: String
  ) {
    allFeedbacks(
      offset: $offset
      before: $before
      after: $after
      first: $first
      last: $last
      issueType: $issueType
      createdAtRange: $createdAtRange
      createdBy: $createdBy
      feedbackId: $feedbackId
      orderBy: $orderBy
      program: $program
      isActiveProgram: $isActiveProgram
    ) {
      totalCount
      pageInfo {
        startCursor
        endCursor
      }
      edges {
        cursor
        node {
          id
          unicefId
          issueType
          householdLookup {
            id
            unicefId
          }
          createdAt
          createdBy {
            id
            firstName
            lastName
            email
          }
          linkedGrievance {
            id
            unicefId
            category
          }
          program {
            id
            name
          }
        }
      }
    }
  }
`;
