import { gql } from 'apollo-boost';

export const AllPaymentRecords = gql`
  query AllPaymentRecords($cashPlan: ID!, $after: String, $first: Int) {
    allPaymentRecords(cashPlan: $cashPlan, after: $after, first: $first) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        cursor
        node {
          id
          createdAt
          updatedAt
          name
          startDate
          endDate
          cashAssistId
          deliveryType
          household {
            householdCaId
          }
        }
      }
      totalCount
      edgeCount
    }
  }
`;
