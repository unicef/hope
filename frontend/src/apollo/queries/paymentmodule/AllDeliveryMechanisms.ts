import { gql } from '@apollo/client';

export const AllDeliveryMechanisms = gql`
  query AllDeliveryMechanisms {
    allDeliveryMechanisms {
      name
      value
    }
  }
`;
