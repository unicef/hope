import { gql } from 'apollo-boost';

export const CREATE_PROGRAM_MUTATION = gql`
  mutation setSteficonRuleOnTargetPopulation($input: SetSteficonRuleOnTargetPopulationMutationInput!){
    setSteficonRuleOnTargetPopulation(input:$input){
      targetPopulation{
        ...targetPopulationDetailed
      }
    }
  }

`;
