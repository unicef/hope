import { gql } from 'apollo-boost';

export const targetPopulationMinimal = gql`
  fragment targetPopulationMinimal on TargetPopulationNode {
    id
    name
    status
    createdAt
    updatedAt
    candidateListTotalHouseholds
    finalListTotalHouseholds
    createdBy {
      firstName
      lastName
    }
  }
`;
export const targetPopulationDetailed = gql`
  fragment targetPopulationDetailed on TargetPopulationNode {
    id
    name
    status
    candidateListTotalHouseholds
    candidateListTotalIndividuals
    finalListTotalHouseholds
    finalListTotalIndividuals
    steficonRule {
      id
      name
    }
    vulnerabilityScoreMin
    vulnerabilityScoreMax
    approvedAt
    finalizedAt
    finalizedBy {
      firstName
      lastName
    }
    program {
      id
      name
      startDate
      endDate
      status
      caId
      description
      budget
      frequencyOfPayments
      populationGoal
      sector
      totalNumberOfHouseholds
      individualDataNeeded
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
        individualsFiltersBlocks {
          individualBlockFilters {
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
`;
