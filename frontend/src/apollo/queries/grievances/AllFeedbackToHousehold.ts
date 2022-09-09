import { gql } from 'apollo-boost';

export const AllFeedbackToHousehold = gql`
  query AllFeedbackToHousehold($ticket: UUID!) {
    allFeedbackToHousehold(ticket: $ticket) {
      edges {
        node {
          id
          individual {
            fullName
          }
          createdBy {
            firstName
            lastName
          }
          createdAt
          message
          kind
        }
      }
    }
  }
`;
