import { gql } from 'apollo-boost';

export const CashPlan = gql`
  query CashPlan($id: ID!) {
    cashPlan(id: $id) {
      id
      name
      startDate
      endDate
      status
      cashAssistId
      dispersionDate
      targetPopulation {
        name
      }
      paymentRecords {
        totalCount
        edgeCount
      }
    }
  }
`;
