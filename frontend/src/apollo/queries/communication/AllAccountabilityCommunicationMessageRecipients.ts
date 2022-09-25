import { gql } from 'apollo-boost';

export const AllAccountabilityCommunicationMessageRecipients = gql`
  query AllAccountabilityCommunicationMessageRecipients(
    $offset: Int
    $before: String
    $after: String
    $first: Int
    $last: Int
    $messageId: String!
    $recipientId: String
    $fullName: String
    $phoneNo: String
    $sex: String
    $orderBy: String
  ) {
    allAccountabilityCommunicationMessageRecipients(
      offset: $offset
      before: $before
      after: $after
      first: $first
      last: $last
      messageId: $messageId
      recipientId: $recipientId
      fullName: $fullName
      phoneNo: $phoneNo
      sex: $sex
      orderBy: $orderBy
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      totalCount
      edgeCount
      edges {
        cursor
        node {
          id
          household {
            id
            unicefId
            headOfHousehold {
              id
              fullName
            }
            size
            status
            admin2 {
              id
              name
            }
            residenceStatus
            lastRegistrationDate
          }
        }
      }
    }
  }
`;
