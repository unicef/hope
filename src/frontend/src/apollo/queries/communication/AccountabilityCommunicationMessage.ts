import { gql } from '@apollo/client';

export const AccountabilityCommunicationMessage = gql`
  query AccountabilityCommunicationMessage($id: ID!) {
    accountabilityCommunicationMessage(id: $id) {
      id
      unicefId
      adminUrl
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
