import { graphql } from "react-relay";

export const allProgramsQuery = graphql`
    query AllProgramsQuery {
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
