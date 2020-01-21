import { gql } from 'apollo-boost';

export const StatusChoices = gql`
    query StatusChoices {
        programStatusChoices
    }
`