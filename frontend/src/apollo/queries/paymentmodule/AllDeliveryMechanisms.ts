import { gql } from 'apollo-boost';

export const AllDeliveryMechanisms = gql`
  query AllDeliveryMechanisms {
    allDeliveryMechanisms {
      name
      value
    }
  }
`;
