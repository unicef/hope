import { gql } from '@apollo/client';

export const AllSteficonRules = gql`
  query AllSteficonRules(
    $enabled: Boolean
    $deprecated: Boolean
    $type: String!
  ) {
    allSteficonRules(enabled: $enabled, deprecated: $deprecated, type: $type) {
      edges {
        node {
          id
          name
        }
      }
    }
  }
`;
