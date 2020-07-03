import { gql } from 'apollo-boost';

export const CHECK_AGAINST_IMPORT_SANCTION_LIST = gql`
  mutation CheckAgainstSanctionList($file: Upload!) {
    checkAgainstSanctionList(file: $file) {
      errors {
        header
        message
        rowNumber
      }
    }
  }
`;
