import { gql } from 'apollo-boost';

export const RegistrationChoices = gql`
    query registrationChoices {
        registrationDataStatusChoices {
            name
            value
        },
    }
`