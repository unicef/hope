import { gql } from 'apollo-boost';

export const SamplingChoices = gql`
  query cashPlanVerificationSamplingChoices {
    cashPlanVerificationSamplingChoices {
      name
      value
    }
  }
`;
