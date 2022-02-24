import { gql } from 'apollo-boost';

export const PaymentVerificationChoices = gql`
  query paymentVerificationChoices {
    paymentVerificationStatusChoices {
      name
      value
    }
    cashPlanVerificationVerificationMethodChoices {
      name
      value
    }
  }
`;
