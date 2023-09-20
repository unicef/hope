import { gql } from 'apollo-boost';

export const PROGRAM_CYCLE_QUERY = gql`
  query ProgramCycle($id: ID!) {
    programCycle(id: $id) {
      id
      unicefId
      isRemoved
      createdAt
      updatedAt
      lastSyncAt
      version
      name
      status
      startDate
      endDate
      totalDeliveredQuantityUsd
      totalUndeliveredQuantityUsd
      totalEntitledQuantityUsd
      program {
        id
        startDate
        endDate
      }
    }
  }
`;
