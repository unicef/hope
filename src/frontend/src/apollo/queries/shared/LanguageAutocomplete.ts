import { gql } from '@apollo/client';

export const LanguageAutocomplete = gql`
  query LanguageAutocomplete($first: Int, $code: String) {
    allLanguages(first: $first, code: $code) {
      edges {
        cursor
        node {
          english
          code
        }
      }
    }
  }
`;
