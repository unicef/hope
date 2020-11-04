import { gql } from 'apollo-boost';

export const AllHouseholds = gql`
  query AllSteficonRules{
    allSteficonRules{
      edges{
        node{
          id
          name
        }
      }
    }
  }
`;
