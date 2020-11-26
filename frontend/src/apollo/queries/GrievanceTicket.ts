import { gql } from 'apollo-boost';

export const GrievanceTicket = gql`
  query GrievanceTicket($id: ID!) {
    grievanceTicket(id: $id) {
      id
      status
      category
      consent
      createdBy {
        id
        firstName
        lastName
        email
      }
      createdAt
      updatedAt
      description
      language
      admin
      area
      assignedTo {
        id
        firstName
        lastName
        email
      }
      individual {
        ...individualDetailed
        householdsAndRoles {
          individual {
            id
            unicefId
          }
          household {
            id
            unicefId
          }
          role
        }
      }
      household {
        ...householdDetailed
      }
      paymentRecord {
        id
      }
      relatedTickets {
        id
        status
        household {
          id
          unicefId
        }
      }
      addIndividualTicketDetails {
        id
        individualData
        approveStatus
        household {
          id
          unicefId
        }
      }
      individualDataUpdateTicketDetails {
        id
        individual {
          ...individualDetailed
        }
        individualData
      }
      householdDataUpdateTicketDetails {
        id
        household {
          ...householdDetailed
        }
        householdData
      }
      issueType
      ticketNotes {
        edges {
          node {
            id
            createdAt
            updatedAt
            description
            createdBy {
              id
              firstName
              lastName
              email
            }
          }
        }
      }
    }
  }
`;
