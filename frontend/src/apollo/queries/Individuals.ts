import { gql } from 'apollo-boost';

export const INDIVIDUALS_QUERY = gql`
  query Individual($id: ID!) {
    individual(id: $id) {
      id
      createdAt
      individualCaId
      fullName
      firstName
      lastName
      sex
      dob
      estimatedDob
      nationality
      martialStatus
      phoneNumber
      identificationType
      identificationNumber
      household {
        id
        address
        location {
          id
          title
          level
        }
      }
      headingHousehold {
        id
        headOfHousehold {
          id
        }
      }
    }
  }
`;
