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
      paymentPlan {
        id
        unicefId
        name
      }
      createdAt
      registrationDataImport {
        id
        name
      }
      title
      body
    }
  }
`;
