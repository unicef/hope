import { gql } from '@apollo/client';

export const CREATE_FEEDBACK_TICKET_MUTATION = gql`
  mutation CreateFeedbackTicket($input: CreateFeedbackInput!) {
    createFeedback(input: $input) {
      feedback {
        id
      }
    }
  }
`;
