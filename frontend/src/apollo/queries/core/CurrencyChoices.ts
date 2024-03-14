import { gql } from '@apollo/client';

export const CurrencyChoices = gql`
  query currencyChoices {
    currencyChoices {
      name
      value
    }
  }
`;
