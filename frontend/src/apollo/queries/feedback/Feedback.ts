import { gql } from 'apollo-boost';

export const Feedback = gql`
  query Feedback($id: ID!) {
    feedback(id: $id) {
      id
      unicefId
      issueType
      householdLookup {
        id
        unicefId
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
      }
    }
  }
`;
