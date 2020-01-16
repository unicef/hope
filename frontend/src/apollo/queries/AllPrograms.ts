import { gql } from 'apollo-boost';

export const AllPrograms = gql`
    query AllPrograms {
        allPrograms{
            pageInfo{
                hasNextPage
                hasPreviousPage
                endCursor
                startCursor
            }
            edges {
                node {
                    id
                    name
                    startDate
                    endDate
                    status
                    programCaId
                    description
                    budget
                }
            }
        }
    }
`;
