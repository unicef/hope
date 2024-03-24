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
      partners {
        id
        name
        areaAccess
        adminAreas {
          ids
          level
          totalCount
        }
      }
    }
  }
`;
