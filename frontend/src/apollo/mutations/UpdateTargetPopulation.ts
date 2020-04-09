import { gql } from 'apollo-boost';

export const UpdateTP = gql`
  mutation UpdateTP($input: UpdateTargetPopulationInput!) {
    updateTargetPopulation(input: $input) {
      targetPopulation {
        id
        name
        status
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
