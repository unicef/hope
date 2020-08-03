import { gql } from 'apollo-boost';

export const ALL_RAPIDPRO_FLOWS_QUERY = gql`
  query AllRapidProFlows($businessAreaSlug: String!) {
    allRapidProFlows(businessAreaSlug: $businessAreaSlug) {
      id
      name
    }
  }
`;
