import {gql} from 'apollo-boost';

export const AllSteficonRules = gql`
  query AllSteficonRules($enabled: Boolean, $deprecated: Boolean) {
    allSteficonRules(enabled: $enabled, deprecated: $deprecated) {
      edges {
        node {
          id
          name
        }
      }
    }
  }
`;
