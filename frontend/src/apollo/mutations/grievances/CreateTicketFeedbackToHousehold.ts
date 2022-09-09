import { gql } from 'apollo-boost';

export const CREATE_FEEDBACK_TO_HOUSEHOLD = gql`
  mutation CreateTicketFeedbackToHousehold(
    $feedback: CreateFeedbackToHouseholdInput!
  ) {
    createFeedbackToHousehold(feedback: $feedback) {
      feedbackToHousehold {
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
`;
