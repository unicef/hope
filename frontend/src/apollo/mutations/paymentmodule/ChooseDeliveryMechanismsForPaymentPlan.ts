import { gql } from 'apollo-boost';

export const CHOOSE_DELIVERY_MECHANISMS_FOR_PAYMENT_PLAN = gql`
  mutation ChooseDeliveryMechForPaymentPlan(
    $input: ChooseDeliveryMechanismsForPaymentPlanInput!
  ) {
    chooseDeliveryMechanismsForPaymentPlan(input: $input) {
      paymentPlan {
        id
        deliveryMechanisms {
          id
          name
          fsp {
            id
            name
          }
        }
      }
    }
  }
`;
