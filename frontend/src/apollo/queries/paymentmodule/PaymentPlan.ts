import { gql } from 'apollo-boost';

export const PaymentPlan = gql`
  query PaymentPlan($id: ID!) {
    paymentPlan(id: $id) {
      isRemoved
      unicefId
      id
      createdAt
      statusDate
      startDate
      endDate
      exchangeRate
      totalEntitledQuantity
      totalEntitledQuantityUsd
      totalEntitledQuantityRevised
      totalEntitledQuantityRevisedUsd
      totalDeliveredQuantity
      totalDeliveredQuantityUsd
      totalUndeliveredQuantity
      totalUndeliveredQuantityUsd
      status
      currency
      currencyName
      dispersionStartDate
      dispersionEndDate
      femaleChildrenCount
      maleChildrenCount
      femaleAdultsCount
      maleAdultsCount
      totalHouseholdsCount
      totalIndividualsCount
      businessArea {
        id
        slug
        code
        name
        longName
      }
      program {
        isRemoved
        id
        createdAt
        updatedAt
        version
        name
        status
        startDate
        endDate
        description
        caId
        caHashId
        budget
      }
      createdBy {
        id
        username
        firstName
        lastName
      }
      targetPopulation {
        name
        id
      }
    }
  }
`;
