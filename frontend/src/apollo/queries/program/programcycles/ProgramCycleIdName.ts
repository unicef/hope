import { gql } from 'apollo-boost';

export const PROGRAM_CYCLE_ID_NAME_QUERY = gql`
  query ProgramCycleIdName($id: ID!) {
    programCycle(id: $id) {
      id
      unicefId
      name
    }
  }
`;
