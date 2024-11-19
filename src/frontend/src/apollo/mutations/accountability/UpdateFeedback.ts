import { gql } from '@apollo/client';

export const UPDATE_FEEDBACK_TICKET_MUTATION = gql`
  mutation UpdateFeedbackTicket($input: UpdateFeedbackInput!) {
    updateFeedback(input: $input) {
      feedback {
        id
        unicefId
        issueType
        householdLookup {
          id
          unicefId
          headOfHousehold {
            id
            fullName
          }
        }
        individualLookup {
          id
          unicefId
        }
        program {
          id
          name
        }
        createdBy {
          id
          firstName
          lastName
          username
          email
        }
        createdAt
        updatedAt
        admin2 {
          id
          name
        }
        area
        language
        description
        comments
        linkedGrievance {
          id
          unicefId
        }
      }
    }
  }
`;
