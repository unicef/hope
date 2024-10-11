import { gql } from '@apollo/client';

export const targetPopulationMinimal = gql`
  fragment targetPopulationMinimal on TargetPopulationNode {
    id
    name
    status
    createdAt
    updatedAt
    totalHouseholdsCount
    totalHouseholdsCountWithValidPhoneNo
    totalIndividualsCount
    __typename
    program {
      id
      name
      __typename
    }
    createdBy {
      id
      firstName
      lastName
      __typename
    }
  }
`;
export const targetPopulationDetailed = gql`
  fragment targetPopulationDetailed on TargetPopulationNode {
    id
    name
    status
    adminUrl
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
      __typename
      id
      rule {
        __typename
        id
        name
      }
    }
    vulnerabilityScoreMin
    vulnerabilityScoreMax
    changeDate
    finalizedAt
    finalizedBy {
      __typename
      id
      firstName
      lastName
    }
    program {
      __typename
      id
      name
      status
      startDate
      endDate
      isSocialWorkerProgram
    }
    programCycle {
      __typename
      id
      title
    }
    createdBy {
      __typename
      id
      email
      firstName
      lastName
    }
    hasEmptyCriteria
    hasEmptyIdsCriteria
    targetingCriteria {
      __typename
      id
      flagExcludeIfActiveAdjudicationTicket
      flagExcludeIfOnSanctionList
      householdIds
      individualIds
      rules {
        __typename
        id
        individualsFiltersBlocks {
          __typename
          individualBlockFilters {
            __typename

            id
            fieldName
            flexFieldClassification
            roundNumber
            arguments
            comparisonMethod
            fieldAttribute {
              __typename
              id
              name
              labelEn
              type
              choices {
                value
                labelEn
              }
              pduData {
                id
                subtype
                numberOfRounds
                roundsNames
              }
            }
          }
        }
        filters {
          __typename
          id
          fieldName
          flexFieldClassification
          roundNumber
          arguments
          comparisonMethod
          fieldAttribute {
            __typename
            id
            name
            labelEn
            type
            choices {
              value
              labelEn
            }
            pduData {
              id
              subtype
              numberOfRounds
              roundsNames
            }
          }
        }
      }
    }
  }
`;
