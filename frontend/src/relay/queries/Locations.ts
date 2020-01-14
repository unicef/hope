import { graphql } from "react-relay";

export const locationsQuery = graphql`
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
