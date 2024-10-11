import { gql } from '@apollo/client';

export const grievanceTicketDetailed = gql`
  fragment grievanceTicketDetailed on GrievanceTicketNode {
    id
    unicefId
    status
    category
    consent
    partner {
      id
      name
    }
    businessArea {
      postponeDeduplication
    }
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
    admin2 {
      id
      name
      pCode
    }
    area
    assignedTo {
      id
      firstName
      lastName
      email
    }
    adminUrl
    individual {
      ...individualDetailed
      householdsAndRoles {
        individual {
          id
          unicefId
          fullName
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
      caId
      deliveredQuantity
      entitlementQuantity
      objType
      parent {
        id
        unicefId
        objType
      }
      verification {
        id
      }
    }
    relatedTickets {
      id
      unicefId
      status
      household {
        id
        unicefId
      }
    }
    linkedTickets {
      id
      unicefId
      category
      status
      household {
        id
        unicefId
      }
    }
    existingTickets {
      id
      category
      unicefId
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
      roleReassignData
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
    deleteHouseholdTicketDetails {
      id
      approveStatus
      reasonHousehold {
        id
        unicefId
      }
    }
    systemFlaggingTicketDetails {
      id
      approveStatus
      roleReassignData
      goldenRecordsIndividual {
        id
        duplicate
        fullName
        birthDate
        lastRegistrationDate
        documents {
          edges {
            node {
              id
              type {
                label
                key
              }
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
      id
      newStatus
      oldReceivedAmount
      newReceivedAmount
      approveStatus
      paymentVerificationStatus
      hasMultiplePaymentVerifications
      paymentVerification {
        id
        receivedAmount
      }
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
      extraData {
        goldenRecords {
          hitId
          proximityToScore
          score
        }
        possibleDuplicate {
          hitId
          proximityToScore
          score
        }
        dedupEngineSimilarityPair {
          similarityScore
          individual1 {
            unicefId
            fullName
            photo
          }
          individual2 {
            unicefId
            fullName
            photo
          }
        }
      }
      goldenRecordsIndividual {
        id
        unicefId
        documents {
          edges {
            node {
              id
              country
              type {
                label
                key
              }
              documentNumber
              photo
            }
          }
        }
        household {
          id
          unicefId
          village
          admin2 {
            id
            name
          }
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
        documents {
          edges {
            node {
              id
              country
              type {
                label
                key
              }
              documentNumber
              photo
            }
          }
        }
        unicefId
        lastRegistrationDate
        household {
          unicefId
          id
          village
          admin2 {
            id
            name
          }
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
      isMultipleDuplicatesVersion
      possibleDuplicates {
        id
        documents {
          edges {
            node {
              id
              country
              type {
                label
                key
              }
              documentNumber
              photo
            }
          }
        }
        unicefId
        lastRegistrationDate
        household {
          unicefId
          id
          village
          admin2 {
            id
            name
          }
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
            fullName
          }
          household {
            id
            unicefId
          }
          id
          role
        }
      }
      selectedDuplicates {
        ...individualDetailed
        household {
          ...householdDetailed
        }
        householdsAndRoles {
          individual {
            id
            unicefId
            fullName
          }
          household {
            id
            unicefId
          }
          id
          role
        }
      }
      selectedDistinct {
        ...individualDetailed
        household {
          ...householdDetailed
        }
        householdsAndRoles {
          individual {
            id
            unicefId
            fullName
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
    priority
    urgency
    programs {
      name
      id
    }
    comments
    documentation {
      id
      createdAt
      updatedAt
      name
      createdBy {
        id
        firstName
        lastName
        email
      }
      fileSize
      contentType
      filePath
      fileName
    }
  }
`;
