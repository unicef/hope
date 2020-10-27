import { gql } from 'apollo-boost';

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
