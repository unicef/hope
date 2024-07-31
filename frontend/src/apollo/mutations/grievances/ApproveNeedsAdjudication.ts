import { gql } from '@apollo/client';

export const ApproveNeedsAdjudication = gql`
  mutation ApproveNeedsAdjudication(
    $grievanceTicketId: ID!
    $selectedIndividualId: ID
    $duplicateIndividualIds: [ID]
    $distinctIndividualIds: [ID]
    $clearIndividualIds: [ID]
  ) {
    approveNeedsAdjudication(
      grievanceTicketId: $grievanceTicketId
      selectedIndividualId: $selectedIndividualId
      duplicateIndividualIds: $duplicateIndividualIds
      distinctIndividualIds: $distinctIndividualIds
      clearIndividualIds: $clearIndividualIds
    ) {
      grievanceTicket {
        id
        status
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
      }
    }
  }
`;
