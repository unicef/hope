import { graphql } from 'react-relay';

export const ProgramQuery = graphql`
  query ProgramQuery($id: ID!, $after: String) {
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
            cashAssistId
            numberOfHouseholds
            
          }
        }
      }
    }
  }
`;
