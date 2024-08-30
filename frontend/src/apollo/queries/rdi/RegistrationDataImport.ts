import { gql } from '@apollo/client';

export const REGISTRATION_DATA_IMPORT_QUERY = gql`
  query RegistrationDataImport($id: ID!) {
    registrationDataImport(id: $id) {
      ...registrationDetailed
    }
  }
`;
