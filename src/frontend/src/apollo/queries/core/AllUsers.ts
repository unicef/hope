import { gql } from '@apollo/client';

export const ALL_USERS_QUERY = gql`
  query AllUsers(
    $search: String
    $status: [String]
    $partner: [String]
    $roles: [String]
    $businessArea: String!
    $program: String
    $first: Int
    $last: Int
    $after: String
    $before: String
    $orderBy: String
  ) {
    allUsers(
      search: $search
      status: $status
      partner: $partner
      roles: $roles
      businessArea: $businessArea
      program: $program
      first: $first
      last: $last
      after: $after
      before: $before
      orderBy: $orderBy
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        endCursor
        startCursor
      }
      edges {
        node {
          id
          firstName
          lastName
          username
          email
          isActive
          lastLogin
          status
          partner {
            name
          }
          userRoles {
            businessArea {
              name
            }
            program {
              id
              name
            }
            role {
              name
              permissions
            }
          }
          partnerRoles {
            businessArea {
              name
            }
            program {
              id
              name
            }
            role {
              name
              permissions
            }
          }
        }
        cursor
      }
      totalCount
      edgeCount
    }
  }
`;
