import { gql } from '@apollo/client';

export const ACCOUNTABILITY_COMMUNICATION_MESSAGE_SAMPLE_SIZE = gql`
  query AccountabilityCommunicationMessageSampleSize(
    $input: GetAccountabilityCommunicationMessageSampleSizeInput!
  ) {
    accountabilityCommunicationMessageSampleSize(input: $input) {
      numberOfRecipients
      sampleSize
    }
  }
`;
