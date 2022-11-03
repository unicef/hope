import { gql } from 'apollo-boost';

export const AccountabilityCommunicationMessage = gql`
  query AccountabilityCommunicationMessage($id: ID!) {
    accountabilityCommunicationMessage(id: $id) {
      id
      unicefId
      createdBy {
        id
        firstName
        lastName
        email
      }
      createdAt
      targetPopulation {
        id
        name
      }
      registrationDataImport {
        id
        name
      }
      title
      body
    }
  }
`;
