import { gql } from 'apollo-boost';

export const DELETE_PROGRAM_CYCLE = gql`
  mutation DeleteProgramCycle($programCycleId: ID!) {
    deleteProgramCycle(programCycleId: $programCycleId) {
      program {
        id
        cycles {
          edges {
            node {
              id
              unicefId
              name
              status
              totalEntitledQuantityUsd
              totalUndeliveredQuantityUsd
              totalUndeliveredQuantityUsd
              startDate
              endDate
            }
          }
        }
      }
    }
  }
`;
