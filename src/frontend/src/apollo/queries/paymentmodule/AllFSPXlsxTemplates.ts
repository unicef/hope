import { gql } from '@apollo/client';

export const ALL_FSP_XLSX_TEMPLATES = gql`
  query AllFinancialServiceProviderXlsxTemplates($businessArea: String!) {
    allFinancialServiceProviderXlsxTemplates(businessArea: $businessArea) {
      edges {
        node {
          id
          name
        }
      }
    }
  }
`;