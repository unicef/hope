import { gql } from 'apollo-boost';

export const RERUN_DEDUPE = gql`
  mutation RerunDedupe($registrationDataImportDatahubId: ID!) {
    rerunDedupe(
      registrationDataImportDatahubId: $registrationDataImportDatahubId
    ) {
      ok
    }
  }
`;
