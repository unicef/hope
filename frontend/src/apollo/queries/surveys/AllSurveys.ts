import { gql } from 'apollo-boost';

export const AllSurveys = gql`
  query AllSurveys(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $program: ID!
    $targetPopulation: ID
    $createdAtRange: String
    $createdBy: ID
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
      targetPopulation: $targetPopulation
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
