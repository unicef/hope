import { gql } from '@apollo/client';

export const TARGET_POPULATION_QUERY = gql`
  query TargetPopulation($id: ID!) {
    paymentPlan(id: $id) {
      id
      version
      name
      status
      buildStatus
      adminUrl
      deliveryMechanism {
        id
        name
        code
      }
      financialServiceProvider {
        id
        name
      }
      failedWalletValidationCollectorsIds
      totalHouseholdsCount
      totalIndividualsCount
      femaleChildrenCount
      femaleAdultsCount
      maleChildrenCount
      maleAdultsCount
      excludedIds
      exclusionReason
      vulnerabilityScoreMin
      vulnerabilityScoreMax
      steficonRuleTargeting {
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
          householdIds
          individualIds
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
          collectorsFiltersBlocks {
            __typename
            id
            createdAt
            updatedAt
            collectorBlockFilters {
              __typename
              id
              createdAt
              updatedAt
              fieldName
              comparisonMethod
              flexFieldClassification
              arguments
              labelEn
            }
          }
          householdsFiltersBlocks {
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
  }
`;
