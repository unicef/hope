import { gql } from 'apollo-boost';

export const ProgrammeChoiceData = gql`
    query ProgrammeChoiceData {
        programFrequencyOfPaymentsChoices,
        programScopeChoices,
        programSectorChoices,
        programStatusChoices
    }
`