import { gql } from '@apollo/client';

export const AllPduFields = gql`
  query AllPduFields($businessAreaSlug: String!, $programId: String!) {
    allPduFields(businessAreaSlug: $businessAreaSlug, programId: $programId) {
      id
      name
      labelEn
      pduData {
        id
        numberOfRounds
      }
    }
  }
`;
