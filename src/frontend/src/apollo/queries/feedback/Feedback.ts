import { gql } from '@apollo/client';

export const Feedback = gql`
  query Feedback($id: ID!) {
    feedback(id: $id) {
      id
      unicefId
      issueType
      adminUrl
      householdLookup {
        id
        unicefId
        admin2 {
          id
          name
          pCode
        }
        headOfHousehold {
          id
          fullName
        }
      }
      individualLookup {
        id
        unicefId
      }
      program {
        id
        name
      }
      createdBy {
        id
        firstName
        lastName
        username
        email
      }
      createdAt
      updatedAt
      admin2 {
        id
        name
      }
      area
      language
      description
      comments
      linkedGrievance {
        id
        unicefId
        category
      }
      feedbackMessages {
        edges {
          node {
            id
            createdAt
            updatedAt
            description
            createdBy {
              id
              firstName
              lastName
              username
              email
            }
          }
        }
      }
    }
  }
`;
