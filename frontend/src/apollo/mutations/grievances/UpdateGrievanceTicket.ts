import { gql } from '@apollo/client';

export const UPDATE_GRIEVANCE_TICKET_MUTATION = gql`
  mutation UpdateGrievance($input: UpdateGrievanceTicketInput!) {
    updateGrievanceTicket(input: $input) {
      grievanceTicket {
        id
      }
    }
  }
`;
