import { gql } from 'apollo-boost';

export const PAYMENT_PLAN_QUERY = gql`
  query PaymentPlan($id: ID!) {
    paymentPlan(id: $id) {
      id
      version
      unicefId
      status
      canCreateFollowUp
      backgroundActionStatus
      canCreatePaymentVerificationPlan
      availablePaymentRecordsCount
      bankReconciliationSuccess
      bankReconciliationError
      createdBy {
        id
        firstName
        lastName
        email
      }
      programCycle {
        id
        unicefId
        name
      }
      program {
        id
        name
        caId
      }
      targetPopulation {
        id
        name
      }
      currency
      currencyName
      startDate
      endDate
      dispersionStartDate
      dispersionEndDate
      femaleChildrenCount
      femaleAdultsCount
      maleChildrenCount
      maleAdultsCount
      totalHouseholdsCount
      totalIndividualsCount
      totalEntitledQuantity
      totalDeliveredQuantity
      totalUndeliveredQuantity
      totalWithdrawnHouseholdsCount
      approvalProcess {
        totalCount
        edgeCount
        edges {
          node {
            id
            sentForApprovalBy {
              id
              firstName
              lastName
              email
            }
            sentForApprovalDate
            sentForAuthorizationBy {
              id
              firstName
              lastName
              email
            }
            sentForAuthorizationDate
            sentForFinanceReleaseBy {
              id
              firstName
              lastName
              email
            }
            sentForFinanceReleaseDate
            approvalNumberRequired
            authorizationNumberRequired
            financeReleaseNumberRequired
            actions {
              approval {
                createdAt
                comment
                info
                createdBy {
                  id
                  firstName
                  lastName
                  email
                }
              }
              authorization {
                createdAt
                comment
                info
                createdBy {
                  id
                  firstName
                  lastName
                  email
                }
              }
              financeRelease {
                createdAt
                comment
                info
                createdBy {
                  id
                  firstName
                  lastName
                  email
                }
              }
              reject {
                createdAt
                comment
                info
                createdBy {
                  id
                  firstName
                  lastName
                  email
                }
              }
            }
            rejectedOn
          }
        }
      }
      steficonRule {
        id
        rule {
          id
          name
        }
      }
      hasPaymentListExportFile
      hasFspDeliveryMechanismXlsxTemplate
      importedFileDate
      importedFileName
      totalEntitledQuantityUsd
      paymentsConflictsCount
      deliveryMechanisms {
        id
        name
        order
        fsp {
          id
          name
          communicationChannel
        }
      }
      volumeByDeliveryMechanism {
        deliveryMechanism {
          id
          name
          order
          fsp {
            id
            name
          }
        }
        volume
        volumeUsd
      }
      verificationPlans {
        totalCount
        edges {
          node {
            id
            unicefId
            status
            sampleSize
            receivedCount
            notReceivedCount
            respondedCount
            verificationChannel
            sampling
            receivedCount
            receivedWithProblemsCount
            rapidProFlowId
            confidenceInterval
            marginOfError
            activationDate
            completionDate
            ageFilter {
              min
              max
            }
            excludedAdminAreasFilter
            sexFilter
            xlsxFileExporting
            hasXlsxFile
            xlsxFileWasDownloaded
            xlsxFileImported
          }
        }
      }
      paymentVerificationSummary {
        id
        createdAt
        updatedAt
        status
        activationDate
        completionDate
      }
      paymentItems {
        totalCount
        edgeCount
        edges {
          node {
            id
            status
          }
        }
      }
      reconciliationSummary {
        deliveredFully
        deliveredPartially
        notDelivered
        unsuccessful
        pending
        numberOfPayments
        reconciled
      }
      excludedHouseholds {
        id
        unicefId
      }
      exclusionReason
      excludeHouseholdError
      isFollowUp
      followUps {
        totalCount
        edges {
          node {
            id
            unicefId
            createdAt
            programCycle {
              id
              unicefId
              name
            }
            paymentItems {
              totalCount
            }
            startDate
            endDate
            dispersionEndDate
            dispersionStartDate
          }
        }
      }
      sourcePaymentPlan {
        id
        unicefId
      }
      unsuccessfulPaymentsCount
    }
  }
`;
