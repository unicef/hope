import { gql } from 'apollo-boost';

export const ImportedIndividualFields = gql`
    query ImportedIndividualFields {
        allCoreFieldAttributes {
            id
            name
            label
            type
            associatedWith
            choices {
                name
                value
            }
        }
    }
`