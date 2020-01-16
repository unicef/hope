import { gql } from 'apollo-boost';

export const Program = gql`
  query Program($id: ID!, $after: String) {
    program(id: $id) {
      id
      name
      startDate
      endDate
      status
      programCaId
      description
      budget
      cashPlans(program: $id, after: $after) {
        pageInfo {
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
        }
        edges{
          node{
            id
            cashAssistId
            numberOfHouseholds
            disbursementDate
          }
        }
      }
    }
  }
`;
