import { gql } from '@apollo/client';

export const USERS_FILTER_QUERY = gql`
  query AllUsersForFilters(
    $businessArea: String!
    $first: Int
    $last: Int
    $after: String
    $before: String
    $orderBy: String
    $search: String
    $isTicketCreator: Boolean
    $isSurveyCreator: Boolean
    $isMessageCreator: Boolean
    $isFeedbackCreator: Boolean
  ) {
    allUsers(
      businessArea: $businessArea
      first: $first
      last: $last
      after: $after
      before: $before
      orderBy: $orderBy
      search: $search
      isTicketCreator: $isTicketCreator
      isSurveyCreator: $isSurveyCreator
      isMessageCreator: $isMessageCreator
      isFeedbackCreator: $isFeedbackCreator
    ) {
      edges {
        node {
          id
          firstName
          lastName
          email
        }
      }
    }
  }
`;
