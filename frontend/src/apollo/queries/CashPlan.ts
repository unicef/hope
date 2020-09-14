import { gql } from 'apollo-boost';

export const CashPlan = gql`
  query CashPlan($id: ID!) {
    cashPlan(id: $id) {
      id
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
      caId
      dispersionDate
      verificationStatus
      verifications {
        edges {
          node {
            id
            status
            sampleSize
            receivedCount
            notReceivedCount
            respondedCount
            verificationMethod
            sampling
            receivedCount
            receivedWithProblemsCount
            rapidProFlowId
            confidenceInterval
            marginOfError
            ageFilter {
              min
              max
            }
            excludedAdminAreasFilter
            sexFilter
          }
        }
      }
      program {
        id
        name
      }
      paymentRecords {
        totalCount
        edgeCount
      }
    }
  }
`;
