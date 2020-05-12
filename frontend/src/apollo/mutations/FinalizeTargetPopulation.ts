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
        approvedAt
        finalizedAt
        finalizedBy {
          firstName
          lastName
        }
        program {
          id
          name
        }
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
        candidateStats {
          childMale
          childFemale
          adultMale
          adultFemale
        }
        finalStats {
          childMale
          childFemale
          adultMale
          adultFemale
        }
      }
    }
  }
`;
