import { gql } from '@apollo/client';

export const programDetails = gql`
  fragment programDetails on ProgramNode {
    id
    name
    programmeCode
    startDate
    endDate
    status
    caId
    caHashId
    description
    budget
    frequencyOfPayments
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
    targetpopulationSet {
      totalCount
    }
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
  }
`;
