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
      fcId
      dpId
      dispersionDate
      assistanceThrough
      cashAssistId
      dispersionDate
      targetPopulation {
        name
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
