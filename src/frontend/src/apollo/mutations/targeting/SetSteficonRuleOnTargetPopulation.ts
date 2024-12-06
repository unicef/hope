import { gql } from '@apollo/client';

export const SET_STEFICON_RULE_ON_TARGET_POPULATION = gql`
  mutation setSteficonRuleOnTargetPopulation(
    $paymentPlanId: ID!
    $steficonRuleId: ID
    $version: BigInt
  ) {
    setSteficonRuleOnTargetPopulation(
      paymentPlanId: $paymentPlanId
      steficonRuleId: $steficonRuleId
      version: $version
    ) {
      paymentPlan {
        id
        name
      }
    }
  }
`;
