import {gql} from 'apollo-boost';

export const CashAssistUrlPrefix = gql`
  query CashAssistUrlPrefix {
    cashAssistUrlPrefix
  }
`;
