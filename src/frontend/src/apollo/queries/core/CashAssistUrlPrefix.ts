import { gql } from '@apollo/client';

export const CashAssistUrlPrefix = gql`
  query CashAssistUrlPrefix {
    cashAssistUrlPrefix
  }
`;
