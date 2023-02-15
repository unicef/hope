import { gql } from 'apollo-boost';

export const PAYMENT_PLAN_QUERY = gql`
  query PaymentPlan($id: ID!) {
    paymentPlan(id: $id) {
      id
      unicefId
      status
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
      approvalNumberRequired
      authorizationNumberRequired
      financeReleaseNumberRequired
      steficonRule {
        id
        rule {
          id
          name
        }
      }
      hasPaymentListExportFile
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
      hasPaymentListExportFile
      importedFileName
      importedFileDate
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
          }
        }
      }
    }
  }
`;
