import { gql } from 'apollo-boost';

export const FinalizeTP = gql`
  mutation FinalizeTP($id: ID!) {
    finalizeTargetPopulation(id: $id) {
      targetPopulation {
        id
        name
        status
        candidateListTotalHouseholds
        candidateListTotalIndividuals
        finalListTotalHouseholds
        finalListTotalIndividuals
        candidateListTargetingCriteria {
          targetPopulationCandidate {
            createdBy {
              firstName
              lastName
            }
            program {
              id
              name
            }
          }
          rules {
            id
            filters {
              fieldName
              isFlexField
              arguments
              comparisionMethod
              fieldAttribute {
                name
                labelEn
                type
                choices {
                  value
                  labelEn
                }
              }
            }
          }
        }
        finalListTargetingCriteria {
          targetPopulationFinal {
            createdBy {
              firstName
              lastName
            }
            program {
              id
              name
            }
          }
          rules {
            id
            filters {
              fieldName
              isFlexField
              arguments
              comparisionMethod
              fieldAttribute {
                name
                labelEn
                type
                choices {
                  value
                  labelEn
                }
              }
            }
          }
        }
      }
    }
  }
`;
