import { gql } from '@apollo/client';

export const SamplingChoices = gql`
  query cashPlanVerificationSamplingChoices {
    cashPlanVerificationSamplingChoices {
      name
      value
    }
  }
`;
