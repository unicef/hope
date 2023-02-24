import { gql } from 'apollo-boost';

export const PaymentPlanStatusChoices = gql`
  query PaymentPlanStatusChoicesQuery {
    paymentPlanStatusChoices {
      name
      value
    }
  }
`;
