import { gql } from 'apollo-boost';

export const PaymentVerificationStatusChoices = gql`
  query paymentVerificationStatusChoices {
    paymentVerificationStatusChoices {
      name
      value
    }
  }
`;
