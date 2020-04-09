import { gql } from 'apollo-boost';
export const ApproveTargetPopulation = gql`
  mutation ApproveTP($id: ID!, $programId: ID!) {
    approveTargetPopulation(id: $id, programId: $programId) {
      targetPopulation {
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
                choices {
                  value
                  labelEn
                }
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
                choices {
                  value
                  labelEn
                }
              }
            }
          }
        }
      }
    }
  }
`;
