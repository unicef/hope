import { gql } from 'apollo-boost';

export const CashPlan = gql`
  query CashPlan($id: ID!) {
    cashPlan(id: $id) {
      id
      name
      startDate
      endDate
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
