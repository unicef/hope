import { gql } from '@apollo/client';

export const PROGRAM_QUERY = gql`
  query Program($id: ID!) {
    program(id: $id) {
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
    }
  }
`;
