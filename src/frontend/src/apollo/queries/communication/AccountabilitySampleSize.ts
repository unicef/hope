import { gql } from '@apollo/client';

export const ACCOUNTABILITY_SAMPLE_SIZE_QUERY = gql`
  query AccountabilitySampleSize($input: AccountabilitySampleSizeInput!) {
    accountabilitySampleSize(input: $input) {
      numberOfRecipients
      sampleSize
    }
  }
`;
