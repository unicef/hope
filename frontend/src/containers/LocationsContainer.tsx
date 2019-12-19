import React from 'react';
import { useQuery } from 'relay-hooks';
import { Locations } from '../relay/queries/Locations';
import { LocationsQuery } from '../__generated__/LocationsQuery.graphql';

export const LocationsContainer: React.FC = () => {
  const { props, error, retry, cached } = useQuery<LocationsQuery>(
    Locations,
    {},
    {},
  );
  if (!props || !props.allLocations) {
    return null;
  }
  return <div>{props.allLocations.edges.map((item) => item.node.country)}</div>;
};
