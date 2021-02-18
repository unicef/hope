import { gql } from 'apollo-boost';

export const ALL_SANCTION_LIST_INDIVIDUALS_QUERY = gql`
  query AllSanctionListIndividuals(
    $referenceNumber: String!
    $first: Int
    $last: Int
    $after: String
    $before: String
    $orderBy: String
    $fullNameContains: String
  ) {
    allSanctionListIndividuals(
      fullName_Startswith: $fullNameContains
      referenceNumber: $referenceNumber
      first: $first
      last: $last
      after: $after
      before: $before
      orderBy: $orderBy
    ) {
      totalCount
      pageInfo {
        hasNextPage
        hasPreviousPage
        endCursor
        startCursor
      }
      edges {
        cursor
        node {
          id
          referenceNumber
          fullName
          listedOn
          documents {
            edges {
              node {
                id
                documentNumber
                typeOfDocument
                issuingCountry
              }
            }
          }
          aliasNames {
            edges {
              node {
                id
                name
              }
            }
          }
          datesOfBirth {
            edges {
              node {
                id
                date
              }
            }
          }
        }
      }
    }
  }
`;
