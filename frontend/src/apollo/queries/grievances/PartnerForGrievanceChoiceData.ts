import { gql } from 'apollo-boost';

export const PartnerForGrievanceChoices = gql`
  query partnerForGrievanceChoices($householdId: ID!, $individualId: ID!) {
    partnerForGrievanceChoices(
      householdId: $householdId
      individualId: $individualId
    ) {
      name
      value
    }
  }
`;
