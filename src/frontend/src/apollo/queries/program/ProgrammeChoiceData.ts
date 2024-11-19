import { gql } from '@apollo/client';

export const ProgrammeChoiceData = gql`
  query ProgrammeChoiceData {
    programFrequencyOfPaymentsChoices {
      name
      value
    }
    programScopeChoices {
      name
      value
    }
    programSectorChoices {
      name
      value
    }
    programStatusChoices {
      name
      value
    }
    dataCollectingTypeChoices {
      name
      value
    }
  }
`;
