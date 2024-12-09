import { gql } from '@apollo/client';

export const PAYMENT_PLAN_QUERY = gql`
  query PaymentPlan($id: ID!) {
    paymentPlan(id: $id) {
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
