import { gql } from 'apollo-boost';

export const AvailableFspsForDeliveryMechanisms = gql`
  query AvailableFspsForDeliveryMechanisms($deliveryMechanisms: [String!]!) {
    availableFspsForDeliveryMechanisms(
      deliveryMechanisms: $deliveryMechanisms
    ) {
      deliveryMechanism
      fsps {
        id
        name
      }
    }
  }
`;
