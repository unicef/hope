import { gql } from 'apollo-boost';

export const allCommunicationMessages = gql`
  query allCommunicationMessages(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $id: UUID
    $title: String
    $title_Icontains: String
    $title_Istartswith: String
    $body_Icontains: String
    $body_Istartswith: String
    $numberOfRecipients: Int
    $numberOfRecipients_Lt: Int
    $numberOfRecipients_Gt: Int
    $businessArea: String!
    $orderBy: String
    $targetPopulation: ID
    $program: String
    $createdAtRange: String
    $createdBy: ID
  ) {
    allCommunicationMessages(
      offset: $offset
      before: $before
      after: $after
      first: $first
      last: $last
      id: $id
      title: $title
      title_Icontains: $title_Icontains
      title_Istartswith: $title_Istartswith
      body_Icontains: $body_Icontains
      body_Istartswith: $body_Istartswith
      numberOfRecipients: $numberOfRecipients
      numberOfRecipients_Lt: $numberOfRecipients_Lt
      numberOfRecipients_Gt: $numberOfRecipients_Gt
      businessArea: $businessArea
      orderBy: $orderBy
      targetPopulation: $targetPopulation
      program: $program
      createdAtRange: $createdAtRange
      createdBy: $createdBy
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
          numberOfRecipients
          createdBy {
            firstName
            lastName
            id
          }
          createdAt
        }
      }
    }
  }
`;
