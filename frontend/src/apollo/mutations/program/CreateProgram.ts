import { gql } from 'apollo-boost';

export const CREATE_PROGRAM_MUTATION = gql`
  mutation CreateProgram($programData: CreateProgramInput!) {
    createProgram(programData: $programData) {
      program {
        id
        name
        programmeCode
        status
        startDate
        endDate
        caId
        budget
        description
        frequencyOfPayments
        sector
        scope
        cashPlus
        populationGoal
        individualDataNeeded
        dataCollectingType {
          id
          code
          label
          active
          individualFiltersAvailable
        }
      }
      validationErrors
    }
  }
`;
