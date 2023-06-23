import { gql } from 'apollo-boost';
export const CREATE_FEEDBACK_MESSAGE = gql`
  mutation CreateFeedbackMsg($input: CreateFeedbackMessageInput!) {
    createFeedbackMessage(input: $input) {
      feedbackMessage {
        id
        createdAt
        updatedAt
        description
        createdBy {
          id
          firstName
          lastName
          username
          email
        }
      }
    }
  }
`;
