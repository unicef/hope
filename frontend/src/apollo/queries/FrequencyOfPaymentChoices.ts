import { gql } from 'apollo-boost';

export const FrequencyOfPaymentChoices = gql`
    query FrequencyOfPayments {
        programFrequencyOfPaymentsChoices
    }
`