import { gql } from '@apollo/client';

export const Survey = gql`
  query Survey($id: ID!) {
    survey(id: $id) {
      id
      unicefId
      category
      title
      adminUrl
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
      rapidProUrl
      sampleFilePath
      hasValidSampleFile
    }
  }
`;
