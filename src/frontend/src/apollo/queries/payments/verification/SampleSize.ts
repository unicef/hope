import { gql } from '@apollo/client';

export const SAMPLE_SIZE_QUERY = gql`
  query SampleSize($input: GetCashplanVerificationSampleSizeInput!) {
    sampleSize(input: $input) {
      paymentRecordCount
      sampleSize
    }
  }
`;
