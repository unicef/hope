import { gql } from '@apollo/client';

export const CREATE_PROGRAM_CYCLE = gql`
  mutation CreateProgramCycle($programCycleData: CreateProgramCycleInput!) {
    createProgramCycle(programCycleData: $programCycleData) {
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
