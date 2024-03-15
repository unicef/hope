import { gql } from '@apollo/client';

export const RERUN_DEDUPE = gql`
  mutation RerunDedupe($registrationDataImportDatahubId: ID!) {
    rerunDedupe(
      registrationDataImportDatahubId: $registrationDataImportDatahubId
    ) {
      ok
    }
  }
`;
