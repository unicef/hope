import { gql } from 'apollo-boost';

export const CREATE_GRIEVANCE_TICKET_MUTATION = gql`
  mutation createGrievanceTicketMutation($input: CreateGrievanceTicketInput!) {
    createGrievanceTicket(input: $input) {
      grievanceTickets {
        id
      }
    }
  }
`;
