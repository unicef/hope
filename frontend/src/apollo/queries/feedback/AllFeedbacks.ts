import { gql } from 'apollo-boost';

export const AllFeedbacks = gql`
  query AllFeedbacks(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $businessAreaSlug: String!
  ) {
    allFeedbacks(
      offset: $offset
      before: $before
      after: $after
      first: $first
      last: $last
      businessAreaSlug: $businessAreaSlug
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
