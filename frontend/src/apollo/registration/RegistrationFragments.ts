import { gql } from 'apollo-boost';

export const registrationMinimal = gql`
  fragment registrationMinimal on RegistrationDataImportNode {
    id
    createdAt
    name
    status
    importDate
    importedBy {
      id
      firstName
      lastName
    }
    dataSource
    numberOfHouseholds
  }
`;

export const registrationDetailed = gql`
  fragment registrationDetailed on RegistrationDataImportNode {
    ...registrationMinimal
    numberOfIndividuals
  }
`;

export const importedHouseholdMinimal = gql`
  fragment importedHouseholdMinimal on ImportedHouseholdNode {
    id
    headOfHousehold {
      id
      fullName
    }
    size
    admin1
    admin2
    registrationDate
  }
`;
export const importedHouseholdDetailed = gql`
  fragment importedHouseholdDetailed on ImportedHouseholdNode {
    ...importedHouseholdMinimal

    residenceStatus
    countryOrigin
    registrationDataImport {
      id
      hctId
      name
    }
  }
`;

export const importedIndividualMinimal = gql`
  fragment importedIndividualMinimal on ImportedIndividualNode {
    id
    fullName
    birthDate
    sex
    role
    relationship
  }
`;

export const importedIndividualDetailed = gql`
  fragment importedIndividualDetailed on ImportedIndividualNode {
    ...importedIndividualMinimal
    givenName
    familyName
    middleName
    estimatedBirthDate

    household {
      id
      admin1
      admin2
      address
    }
    registrationDataImport {
      id
      hctId
      name
    }
    phoneNo
    phoneNoAlternative
  }
`;
