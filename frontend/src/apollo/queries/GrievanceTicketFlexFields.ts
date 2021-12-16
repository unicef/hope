import { gql } from 'apollo-boost';

export const GrievanceTicketFlexFields = gql`
  query GrievanceTicketFlexFields($id: ID!) {
    grievanceTicket(id: $id) {
      id
      individualDataUpdateTicketDetails {
        id
        individualData
      }
      householdDataUpdateTicketDetails {
        id
        householdData
      }
    }
  }
`;
