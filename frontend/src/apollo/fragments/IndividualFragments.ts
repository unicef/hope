import { gql } from 'apollo-boost';

export const individualMinimal = gql`
  fragment individualMinimal on IndividualNode {
    id
    createdAt
    updatedAt
    fullName
    sex
    birthDate
    maritalStatus
    phoneNo
    role
    documents {
      edges {
        node {
          id
          documentNumber
          type {
            country
            label
          }
        }
      }
    }
    household {
      id
      adminArea{
        id
        title
      }
    }
  }
`;

export const individualDetailed = gql`
  fragment individualDetailed on IndividualNode {
    ...individualMinimal
    givenName
    familyName
    estimatedBirthDate
    household {
      id
      address
      countryOrigin
      adminArea {
        id
        title
        level
      }
    }
    headingHousehold {
      id
      headOfHousehold {
        id
      }
    }
    flexFields
  }
`;
