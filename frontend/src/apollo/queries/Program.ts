import { gql } from 'apollo-boost';

export const Program = gql`
  query Program($id: ID!) {
    program(id: $id) {
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
`;
