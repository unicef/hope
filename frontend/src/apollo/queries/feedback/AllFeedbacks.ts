import { gql } from 'apollo-boost';

export const AllFeedbacks = gql`
  query AllFeedbacks(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $businessAreaSlug: String!
    $issueType: String
    $createdAtRange: String
    $createdBy: String
    $feedbackId: String
  ) {
    allFeedbacks(
      offset: $offset
      before: $before
      after: $after
      first: $first
      last: $last
      businessAreaSlug: $businessAreaSlug
      issueType: $issueType
      createdAtRange: $createdAtRange
      createdBy: $createdBy
      feedbackId: $feedbackId
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
          linkedGrievance {
            id
            unicefId
          }
        }
      }
    }
  }
`;
