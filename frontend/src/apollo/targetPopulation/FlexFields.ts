import { gql } from 'apollo-boost';

export const FlexFields = gql`
  query FlexFields {
    allFieldsAttributes(flexField: true) {
      type
      name
      labelEn
    }
  }
`;
