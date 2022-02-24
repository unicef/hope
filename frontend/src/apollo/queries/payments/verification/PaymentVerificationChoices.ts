import { gql } from 'apollo-boost';

export const PaymentVerificationChoices = gql`
  query paymentVerificationChoices {
    paymentVerificationStatusChoices {
      name
      value
    }
    cashPlanVerificationVerificationChannelChoices {
      name
      value
    }
  }
`;
