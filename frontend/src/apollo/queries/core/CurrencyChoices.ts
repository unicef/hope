import { gql } from 'apollo-boost';

export const CurrencyChoices = gql`
  query currencyChoices {
    currencyChoices {
      name
      value
    }
  }
`;
