import { gql } from '@apollo/client';

export const allAccountabilityCommunicationMessages = gql`
  query allAccountabilityCommunicationMessages(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $numberOfRecipients: Int
    $numberOfRecipients_Gte: Int
    $numberOfRecipients_Lte: Int
    $targetPopulation: ID
    $createdBy: ID
    $program: String
    $createdAtRange: String
    $title: String
    $body: String
    $samplingType: String
    $orderBy: String
  ) {
    allAccountabilityCommunicationMessages(
      offset: $offset
      before: $before
      after: $after
      first: $first
      last: $last
      numberOfRecipients: $numberOfRecipients
      numberOfRecipients_Gte: $numberOfRecipients_Gte
      numberOfRecipients_Lte: $numberOfRecipients_Lte
      targetPopulation: $targetPopulation
      createdBy: $createdBy
      program: $program
      createdAtRange: $createdAtRange
      title: $title
      body: $body
      samplingType: $samplingType
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
