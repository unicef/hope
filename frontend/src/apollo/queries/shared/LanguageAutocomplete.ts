import { gql } from 'apollo-boost';

export const LanguageAutocomplete = gql`
  query LanguageAutocomplete($first: Int, $name: String) {
    allLanguages(first: $first, name: $name) {
      edges {
        cursor
        node {
          english
          alpha2
        }
      }
    }
  }
`;
