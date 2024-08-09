import { gql } from '@apollo/client';

export const PDUSUBTYPE_CHOICES_DATA = gql`
  query pduSubtypeChoicesData {
    pduSubtypeChoices {
      value
      displayName
    }
  }
`;
