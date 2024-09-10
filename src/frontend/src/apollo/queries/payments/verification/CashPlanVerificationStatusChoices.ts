import { gql } from '@apollo/client';

export const CashPlanVerificationStatusChoices = gql`
  query cashPlanVerificationStatusChoices {
    cashPlanVerificationStatusChoices {
      name
      value
    }
    paymentRecordDeliveryTypeChoices {
      name
      value
    }
  }
`;
