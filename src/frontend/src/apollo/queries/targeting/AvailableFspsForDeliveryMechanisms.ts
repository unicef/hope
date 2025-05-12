import { gql } from '@apollo/client';

export const AVAILABLE_FSPS_FOR_DELIVERY_MECHANISMS = gql`
  query AvailableFspsForDeliveryMechanisms {
    availableFspsForDeliveryMechanisms {
      deliveryMechanism {
        name
        code
      }
      fsps {
        id
        name
      }
    }
  }
`;
