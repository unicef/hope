import { gql } from 'apollo-boost';

export const CreateCommunicationMessage = gql`
  mutation CreateAccountabilityCommunicationMessage(
    $input: CreateAccountabilityCommunicationMessageInput!
  ) {
    createAccountabilityCommunicationMessage(input: $input) {
      message {
        id
      }
    }
  }
`;
