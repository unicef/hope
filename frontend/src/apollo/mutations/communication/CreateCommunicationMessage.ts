import { gql } from '@apollo/client';

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
