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
          lastRegistrationDate
          documents {
            edges {
              node {
                id
                documentNumber
              }
            }
          }
        }
        sanctionListIndividual {
          id
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
      needsAdjudicationTicketDetails {
        id
        hasDuplicatedDocument
        goldenRecordsIndividual {
          id
          unicefId
          household {
            id
            unicefId
          }
          fullName
          birthDate
          lastRegistrationDate
          sex
          deduplicationGoldenRecordResults {
            hitId
            proximityToScore
            score
          }
        }
        possibleDuplicate {
          id
          unicefId
          lastRegistrationDate
          household {
            unicefId
            id
          }
          fullName
          birthDate
          sex
          deduplicationGoldenRecordResults {
            hitId
            proximityToScore
            score
          }
        }
        selectedIndividual {
          ...individualDetailed
          household {
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
