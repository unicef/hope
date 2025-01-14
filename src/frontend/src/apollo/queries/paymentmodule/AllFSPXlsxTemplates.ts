import { gql } from '@apollo/client';

export const ALL_FSP_XLSX_TEMPLATES = gql`
  query AllFinancialServiceProviderXlsxTemplates {
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
