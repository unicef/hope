import { gql } from '@apollo/client';

export const programDetails = gql`
  fragment programDetails on ProgramNode {
    id
    name
    programmeCode
    startDate
    endDate
    status
    description
    budget
    frequencyOfPayments
    screenBeneficiary
    cashPlus
    populationGoal
    scope
    sector
    totalNumberOfHouseholds
    totalNumberOfHouseholdsWithTpInProgram
    administrativeAreasOfImplementation
    isSocialWorkerProgram
    version
    adminUrl
    dataCollectingType {
      id
      code
      label
      active
      individualFiltersAvailable
      householdFiltersAvailable
      description
      type
    }
    partnerAccess
    partners {
      id
      name
      areaAccess
      areas {
        id
        level
      }
    }
    registrationImports {
      totalCount
    }
    targetPopulationsCount
    pduFields {
      id
      label
      pduData {
        id
        subtype
        numberOfRounds
        roundsNames
      }
    }
    canFinish
    beneficiaryGroup {
      id
      name
      groupLabel
      groupLabelPlural
      memberLabel
      memberLabelPlural
      masterDetail
    }
  }
`;
