import { gql } from '@apollo/client';

export const AllSurveys = gql`
  query AllSurveys(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $program: ID!
    $paymentPlan: ID
    $createdAtRange: String
    $createdBy: String
    $search: String
    $orderBy: String
  ) {
    allSurveys(
      offset: $offset
      before: $before
      after: $after
      first: $first
      last: $last
      program: $program
      paymentPlan: $paymentPlan
      createdAtRange: $createdAtRange
      createdBy: $createdBy
      search: $search
      orderBy: $orderBy
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
          title
          category
          numberOfRecipients
          createdBy {
            id
            firstName
            lastName
            email
          }
          createdAt
        }
      }
    }
  }
`;
