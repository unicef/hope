import { gql } from '@apollo/client';

export const SET_STEFICON_RULE_ON_TP = gql`
  mutation SetSteficonRuleOnTargetPopulation(
    $paymentPlanId: ID!
    $steficonRuleId: ID!
  ) {
    setSteficonRuleOnTargetPopulation(
      paymentPlanId: $paymentPlanId
      steficonRuleId: $steficonRuleId
    ) {
      paymentPlan {
        id
        steficonRule {
          id
          rule {
            id
            name
          }
        }
      }
    }
  }
`;
