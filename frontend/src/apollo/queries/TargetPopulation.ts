import { gql } from 'apollo-boost';

export const TargetPopulation = gql`
  query targetPopulation($id: ID!) {
    targetPopulation(id: $id) {
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
      createdBy {
        firstName
        lastName
      }
      candidateListTargetingCriteria {
        targetPopulationCandidate {
          createdBy {
            firstName
            lastName
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
`;
