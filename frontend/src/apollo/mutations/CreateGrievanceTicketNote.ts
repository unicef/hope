import { gql } from 'apollo-boost';
export const CREATE_GRIEVANCE_TICKET_NOTE = gql`
  mutation CreateGrievanceTicketNote($noteInput: CreateTicketNoteInput!) {
    createTicketNote(noteInput: $noteInput) {
      grievanceTicketNote {
        id
        createdAt
        updatedAt
        createdBy {
          firstName
          lastName
          username
          email
        }
      }
    }
  }
`;
