import { gql } from '@apollo/client';

export const PAYMENT_PLAN_QUERY = gql`
  query PaymentPlan($id: ID!) {
    paymentPlan(id: $id) {
      id
      name
      version
      unicefId
      status
      buildStatus
      canCreateFollowUp
      failedWalletValidationCollectorsIds
      backgroundActionStatus
      canCreatePaymentVerificationPlan
      availablePaymentRecordsCount
      bankReconciliationSuccess
      bankReconciliationError
      exchangeRate
      fspCommunicationChannel
      canExportXlsx
      canDownloadXlsx
      canSendXlsxPassword
      volumeByDeliveryMechanism {
        deliveryMechanism {
          id
          name
          fsp {
            id
            name
          }
        }
        volume
        volumeUsd
      }
      availableFundsCommitments {
        fundsCommitmentNumber
        fundsCommitmentItems {
          id
          paymentPlan {
            id
            name
          }
          fundsCommitmentItem
          recSerialNumber
        }
      }
      fundsCommitments {
        fundsCommitmentNumber
        insufficientAmount
        fundsCommitmentItems {
          id
          fundsCommitmentItem
          recSerialNumber
          wbsElement
          grantNumber
          currencyCode
          commitmentAmountLocal
          commitmentAmountUsd
          totalOpenAmountLocal
          totalOpenAmountUsd
          sponsor
          sponsorName
          fund
          fundsCenter
        }
      }
      deliveryMechanism {
        id
        name
        code
      }
      financialServiceProvider {
        id
        name
      }
      programCycle {
        id
        title
      }
      excludedIds
      createdBy {
        id
        firstName
        lastName
        email
      }
      program {
        id
        name
        status
        isSocialWorkerProgram
        screenBeneficiary
      }
      vulnerabilityScoreMin
      vulnerabilityScoreMax
      adminUrl
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
      steficonRuleTargeting {
        id
        rule {
          id
          name
        }
      }
      hasPaymentListExportFile
      hasFspDeliveryMechanismXlsxTemplate
      canCreateXlsxWithFspAuthCode
      importedFileDate
      importedFileName
      totalEntitledQuantityUsd
      paymentsConflictsCount
      canSendToPaymentGateway
      canSplit
      splitChoices {
        name
        value
      }
      verificationPlans {
        totalCount
        edges {
          node {
            id
            unicefId
            adminUrl
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
      excludedIndividuals {
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
            paymentItems {
              totalCount
            }
          }
        }
      }
      sourcePaymentPlan {
        id
        unicefId
      }
      unsuccessfulPaymentsCount
      supportingDocuments {
        id
        title
        file
      }
      flagExcludeIfActiveAdjudicationTicket
      flagExcludeIfOnSanctionList
      householdIds
      individualIds
      rules {
        __typename
        id
        householdIds
        individualIds
        individualsFiltersBlocks {
          __typename
          individualBlockFilters {
            __typename

            id
            fieldName
            flexFieldClassification
            roundNumber
            arguments
            comparisonMethod
            fieldAttribute {
              __typename
              id
              name
              labelEn
              type
              choices {
                value
                labelEn
              }
              pduData {
                id
                subtype
                numberOfRounds
                roundsNames
              }
            }
          }
        }
        collectorsFiltersBlocks {
          __typename
          id
          createdAt
          updatedAt
          collectorBlockFilters {
            __typename
            id
            createdAt
            updatedAt
            fieldName
            comparisonMethod
            flexFieldClassification
            arguments
            labelEn
          }
        }
        householdsFiltersBlocks {
          __typename
          id
          fieldName
          flexFieldClassification
          roundNumber
          arguments
          comparisonMethod
          fieldAttribute {
            __typename
            id
            name
            labelEn
            type
            choices {
              value
              labelEn
            }
            pduData {
              id
              subtype
              numberOfRounds
              roundsNames
            }
          }
        }
      }
    }
  }
`;
