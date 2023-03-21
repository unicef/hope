import { gql } from 'apollo-boost';

export const SET_STEFICON_RULE_ON_P_P_PAYMENT_LIST = gql`
  mutation SetSteficonRuleOnPPList($paymentPlanId: ID!, $steficonRuleId: ID!) {
    setSteficonRuleOnPaymentPlanPaymentList(
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
