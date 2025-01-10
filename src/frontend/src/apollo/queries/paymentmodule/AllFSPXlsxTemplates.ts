import { gql } from '@apollo/client';

export const ALL_FSP_XLSX_TEMPLATES = gql`
  query allFinancialServiceProviderXlsxTemplates {
    allFinancialServiceProviderXlsxTemplates {
      edges {
        node {
          id
          name
        }
      }
    }
  }
`;
