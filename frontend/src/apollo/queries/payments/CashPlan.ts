import { gql } from 'apollo-boost';

export const CashPlan = gql`
  query CashPlan($id: ID!) {
    cashPlan(id: $id) {
      id
      canCreatePaymentVerificationPlan
      availablePaymentRecordsCount
      name
      startDate
      endDate
      updatedAt
      status
      deliveryType
      fundsCommitment
      downPayment
      dispersionDate
      assistanceThrough
      serviceProvider {
        id
        caId
        fullName
      }
      caId
      caHashId
      dispersionDate
      bankReconciliationSuccess
      bankReconciliationError
      totalNumberOfHouseholds
      # verificationPlans {
      #   totalCount
      #   edges {
      #     node {
      #       id
      #       unicefId
      #       status
      #       sampleSize
      #       receivedCount
      #       notReceivedCount
      #       respondedCount
      #       verificationChannel
      #       sampling
      #       receivedCount
      #       receivedWithProblemsCount
      #       rapidProFlowId
      #       confidenceInterval
      #       marginOfError
      #       activationDate
      #       completionDate
      #       ageFilter {
      #         min
      #         max
      #       }
      #       excludedAdminAreasFilter
      #       sexFilter
      #       xlsxFileExporting
      #       hasXlsxFile
      #       xlsxFileWasDownloaded
      #       xlsxFileImported
      #     }
      #   }
      # }
      # paymentVerificationSummary {
      #   id
      #   createdAt
      #   updatedAt
      #   status
      #   activationDate
      #   completionDate
      # }
      program {
        id
        name
        caId
      }
      paymentItems {
        totalCount
        edgeCount
        edges {
          node {
            targetPopulation {
              id
              name
            }
          }
        }
      }
    }
  }
`;
