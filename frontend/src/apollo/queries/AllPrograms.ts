import { gql } from 'apollo-boost';

export const ALL_PROGRAMS_QUERY = gql`
  query AllPrograms($businessArea: String) {
    allPrograms(businessArea: $businessArea) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        endCursor
        startCursor
      }
      edges {
        node {
          id
          name
          startDate
          endDate
          status
          programCaId
          description
          budget
          frequencyOfPayments
          populationGoal
          sector
          totalNumberOfHouseholds
        }
      }
    }
  }
`;
