import { gql } from 'apollo-boost';

export const CreateCommunicationMessage = gql`
  mutation CreateAccountabilityCommunicationMessage(
    $businessAreaSlug: String!
    $inputs: CreateAccountabilityCommunicationMessageInput!
  ) {
    createAccountabilityCommunicationMessage(businessAreaSlug: $businessAreaSlug, inputs: $inputs) {
      message {
        id
      }
    }
  }
`;
