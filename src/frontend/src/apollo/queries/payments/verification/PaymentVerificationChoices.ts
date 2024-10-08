import { gql } from '@apollo/client';

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
    paymentRecordDeliveryTypeChoices {
      name
      value
    }
  }
`;
