import { gql } from '@apollo/client';

export const DEDUPLICATION_FLAGS_QUERY = gql`
  query DeduplicationFlags {
    canRunDeduplication
    isDeduplicationDisabled
  }
`;
