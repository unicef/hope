import { gql } from 'apollo-boost';

export const PROGRAM_QUERY = gql`
  query Program($id: ID!) {
    program(id: $id) {
      id
      name
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
      individualDataNeeded
      version
      cycles {
        edges {
          node {
            id
            unicefId
            name
            status
            totalEntitledQuantityUsd
            totalUndeliveredQuantityUsd
            totalUndeliveredQuantityUsd
            startDate
            endDate
          }
        }
      }
      dataCollectingType {
        id
        code
        label
        active
        individualFiltersAvailable
      }
    }
  }
`;
