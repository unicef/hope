import { graphql } from "react-relay";

export const Location = graphql`
  query LocationsQuery {
      allLocations{
          edges {
              node {
                  id
                  country
                  name
              }
          }
      }
  }
`;
