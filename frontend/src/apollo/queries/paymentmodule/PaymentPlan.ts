import { gql } from 'apollo-boost';

export const PaymentPlan = gql`
  query PaymentPlan($id: ID!) {
    paymentPlan(id: $id) {
      id
      unicefId
      status
      createdBy {
        id
        firstName
        lastName
        email
      }
      program {
        id
        name
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
    }
  }
`;
