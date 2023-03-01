import { gql } from 'apollo-boost';

export const ASSIGN_FSP_TO_DELIVERY_MECHANISM = gql`
  mutation AssignFspToDeliveryMech($input: AssignFspToDeliveryMechanismInput!) {
    assignFspToDeliveryMechanism(input: $input) {
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
