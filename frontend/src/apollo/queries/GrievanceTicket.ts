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
          id
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
      deleteIndividualTicketDetails {
        id
        roleReassignData
        approveStatus
      }
      systemFlaggingTicketDetails {
        id
        approveStatus
        roleReassignData
        goldenRecordsIndividual {
          id
          fullName
          birthDate
          documents{
            edges{
              node{
                documentNumber
              }
            }
          }
        }
        sanctionListIndividual {
          fullName
          referenceNumber
          
          datesOfBirth {
            edges {
              node {
                id
                date
              }
            }
          }
          documents {
            edges {
              node {
                id
                documentNumber
                typeOfDocument
              }
            }
          }
        }
      }
      paymentVerificationTicketDetails {
        paymentVerificationStatus
        paymentVerifications {
          edges {
            node {
              id
            }
          }
        }
      }
      needsAdjudicationTicketDetails{
        id
        
        goldenRecordsIndividual{
          id
          unicefId
          household{
            id
            unicefId
          }
          fullName
          birthDate
          sex
        }
        possibleDuplicate{
          id
          unicefId
          household{
            unicefId
            id
          }
          fullName
          birthDate
          sex
        }
        selectedIndividual{
          ...individualDetailed
          household{
            ...householdDetailed
          }
          householdsAndRoles {
            individual {
              id
              unicefId
            }
            household {
              id
              unicefId
            }
            id
            role
          }
        }
        roleReassignData
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
