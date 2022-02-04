import { gql } from 'apollo-boost';

export const SAMPLE_SIZE_QUERY = gql`
  query SampleSize($input: GetCashplanVerificationSampleSizeInput!) {
    sampleSize(input: $input) {
      paymentRecordCount
      sampleSize
    }
  }
`;
