import { gql } from 'apollo-boost';

export const CHECK_AGAINST_IMPORT_SANCTION_LIST = gql`
  mutation CheckAgainstSanctionListUpload($file: Upload!) {
    checkAgainstSanctionList(file: $file) {
      errors {
        header
        message
        rowNumber
      }
    }
  }
`;
