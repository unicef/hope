import { gql } from 'apollo-boost';

export const UpdateProgram = gql`
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
          location {
            country
            id
            name
          }
          populationGoal
          scope
          sector
          totalNumberOfHouseholds
          location{
            name
          }
          cashPlus
          frequencyOfPayments
        }
      }
    }
`