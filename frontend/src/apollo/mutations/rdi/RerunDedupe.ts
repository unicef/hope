import { gql } from '@apollo/client';

export const RERUN_DEDUPE = gql`
  mutation RerunDedupe($registrationDataImportId: ID!) {
    rerunDedupe(registrationDataImportId: $registrationDataImportId) {
      ok
    }
  }
`;
