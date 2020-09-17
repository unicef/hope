import { gql } from 'apollo-boost';

export const individualMinimal = gql`
  fragment individualMinimal on IndividualNode {
    id
    createdAt
    updatedAt
    fullName
    sex
    unicefId
    birthDate
    maritalStatus
    phoneNo
    sanctionListPossibleMatch
    deduplicationStatus
    role
    status
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
      unicefId
      status
      adminArea {
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
    pregnant
    status
    documents {
      edges {
        node {
          type {
            label
          }
          documentNumber
        }
      }
    }
    enrolledInNutritionProgramme
    administrationOfRutf
    identities {
      number
      type
    }
    household {
      status
      id
      address
      countryOrigin
      adminArea {
        id
        title
        level
      }
    }
    role
    relationship
    headingHousehold {
      id
      headOfHousehold {
        id
      }
    }
    flexFields
  }
`;
