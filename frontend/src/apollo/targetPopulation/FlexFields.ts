import { gql } from 'apollo-boost';

export const FlexFields = gql`
  query FlexFields {
    allFieldsAttributes(flexField: true) {
      id
      type
      name
      labelEn
    }
  }
`;
