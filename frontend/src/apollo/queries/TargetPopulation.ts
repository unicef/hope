import { gql } from 'apollo-boost';

export const TargetPopulation = gql`
  query targetPopulation($id: ID!) {
    targetPopulation(id: $id) {
      id
      name
      status
      households {
        edges {
          node {
            id
            headOfHousehold {
              fullName
            }
            householdCaId
            location {
              title
            }
          }
        }
      }
      candidateListTargetingCriteria {
        targetPopulationCandidate {
          createdBy {
            firstName
            lastName
          }
          program {
            id
            name
          }
        }
        rules {
          id
          filters {
            fieldName
            isFlexField
            arguments
            comparisionMethod
            fieldAttribute {
              name
              labelEn
              type
            }
          }
        }
      }
      finalListTargetingCriteria {
        targetPopulationFinal {
          createdBy {
            firstName
            lastName
          }
          program {
            id
            name
          }
        }
        rules {
          id
          filters {
            fieldName
            isFlexField
            arguments
            comparisionMethod
            fieldAttribute {
              name
              labelEn
              type
            }
          }
        }
      }
    }
  }
`;
