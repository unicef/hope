import { gql } from '@apollo/client';

export const SET_STEFICON_RULE_ON_P_P_PAYMENT_LIST = gql`
  mutation SetSteficonRuleOnPPList($paymentPlanId: ID!, $steficonRuleId: ID!, $version: BigInt) {
    setSteficonRuleOnPaymentPlanPaymentList(
      paymentPlanId: $paymentPlanId
      steficonRuleId: $steficonRuleId
      version: $version
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
        steficonRuleTargeting {
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
