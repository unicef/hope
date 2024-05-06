import { gql } from '@apollo/client';

export const PaymentPlanStatusChoices = gql`
  query PaymentPlanStatusChoicesQuery {
    paymentPlanStatusChoices {
      name
      value
    }
  }
`;
