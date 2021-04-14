import { gql } from 'apollo-boost';
import {targetPopulationDetailed} from "../fragments/TargetPopulationFragments";

export const TARGET_POPULATION_QUERY = gql`
  query targetPopulation($id: ID!) {
    targetPopulation(id: $id) {
      ...targetPopulationDetailed
    }
  }
  ${targetPopulationDetailed}
`;
