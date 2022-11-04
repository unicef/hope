import { gql } from 'apollo-boost';

export const targetPopulationMinimal = gql`
  fragment targetPopulationMinimal on TargetPopulationNode {
    id
    name
    status
    createdAt
    updatedAt
    totalHouseholdsCount
    totalIndividualsCount
    program {
      id
      name
    }
    createdBy {
      id
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
    buildStatus
    totalHouseholdsCount
    totalIndividualsCount
    childMaleCount
    childFemaleCount
    adultMaleCount
    adultFemaleCount
    caHashId
    excludedIds
    exclusionReason
    steficonRule {
      id
      rule {
        id
        name
      }
    }
    vulnerabilityScoreMin
    vulnerabilityScoreMax
    changeDate
    finalizedAt
    finalizedBy {
      id
      firstName
      lastName
    }
    program {
      id
      name
      status
    }
    createdBy {
      id
      email
      firstName
      lastName
    }
    targetingCriteria {
      rules {
        id
        individualsFiltersBlocks {
          individualBlockFilters {
            fieldName
            isFlexField
            arguments
            comparisonMethod
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
          comparisonMethod
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
`;
