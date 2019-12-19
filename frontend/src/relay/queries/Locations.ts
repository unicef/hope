import { graphql } from "react-relay";

export const Locations = graphql`
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
