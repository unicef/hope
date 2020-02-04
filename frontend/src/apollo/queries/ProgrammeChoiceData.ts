import { gql } from 'apollo-boost';

export const ProgrammeChoiceData = gql`
    query ProgrammeChoiceData {
        programFrequencyOfPaymentsChoices {
            name
            value
        },
        programScopeChoices {
            name
            value
        },
        programSectorChoices {
            name
            value
        },
        programStatusChoices {
            name
            value
        }
    }
`