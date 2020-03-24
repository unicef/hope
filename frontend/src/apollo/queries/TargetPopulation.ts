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
    }
  }
`;
