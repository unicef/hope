import { gql } from 'apollo-boost';

export const REGISTRATION_DATA_IMPORT_QUERY = gql`
  query RegistrationDataImport($id: ID!) {
    registrationDataImport(id: $id) {
      ...registrationFragmentDetailed
    }
  }
`;
