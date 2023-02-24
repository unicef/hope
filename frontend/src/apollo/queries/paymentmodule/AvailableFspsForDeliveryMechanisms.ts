import { gql } from 'apollo-boost';

export const AVAILABLE_FSPS_FOR_DELIVERY_MECHANISMS_QUERY = gql`
query AvailableFspsForDeliveryMechanisms($input: AvailableFspsForDeliveryMechanismsInput!) {
    availableFspsForDeliveryMechanisms(input: $input) {
        deliveryMechanism
        fsps {
            id
            name
        }
    }
}
`