import { gql } from 'apollo-boost';

export const Survey = gql`
  query Survey($id: ID!) {
    survey(id: $id) {
      id
      unicefId
      category
      title
      createdBy {
        id
        firstName
        lastName
        username
        email
      }
      createdAt
      targetPopulation {
        id
        name
      }
      program {
        id
        name
      }
      body
      title
      sampleFilePath
      hasValidSampleFile
    }
  }
`;
