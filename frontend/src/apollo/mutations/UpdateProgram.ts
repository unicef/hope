import { gql } from 'apollo-boost';

export const UPDATE_PROGRAM_MUTATION = gql`
  mutation UpdateProgram($programData: UpdateProgramInput!) {
    updateProgram(programData: $programData) {
      program {
        id
        name
        startDate
        endDate
        status
        programCaId
        description
        budget
        frequencyOfPayments
        cashPlus
        populationGoal
        scope
        sector
        totalNumberOfHouseholds
        administrativeAreasOfImplementation
      }
    }
  }
`;
