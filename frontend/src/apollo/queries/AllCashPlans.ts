// import { graphql } from 'relay-runtime';
//
import { gql } from 'apollo-boost';

export const AllCashPlans = gql`
    query AllCashPlans($program:ID!,$after:String,$count:Int){

        allCashPlans(program: $program, after: $after,first: $count) {
            pageInfo {
                hasNextPage
                hasPreviousPage
                startCursor
                endCursor
            }
            edges{
                cursor
                node{
                    id
                    cashAssistId
                    numberOfHouseholds
                    disbursementDate
                }
            }
        }
    } `;
