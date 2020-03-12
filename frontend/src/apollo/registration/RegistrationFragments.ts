import { gql } from 'apollo-boost';

export const registrationFragmentMinimal = gql`
  fragment registrationFragmentMinimal on RegistrationDataImportNode {
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

export const registrationFragmentDetailed = gql`
  fragment registrationFragmentDetailed on RegistrationDataImportNode {
    ...registrationFragmentMinimal
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
    familySize
    location
    registrationDate
  }
`;
export const importedHouseholdDetailed = gql`
    fragment importedHouseholdDetailed on ImportedHouseholdNode {
        id
        headOfHousehold {
            id
            fullName
        }
        familySize
        location
        registrationDate
        
        residenceStatus
        nationality
        representative{
            id
            fullName
        }
        registrationDataImportId{
            hctId
        }
    }
`;

export const importedIndividualMinimal = gql`
  fragment importedIndividualMinimal on ImportedIndividualNode {
    id
    fullName
    workStatus
    dob
    sex
  }
`;
