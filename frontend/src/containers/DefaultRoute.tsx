import { Redirect } from 'react-router-dom';
import React from 'react';
import { useCachedMe } from '../hooks/useCachedMe';

export function DefaultRoute(): React.ReactElement {
  const { data } = useCachedMe();
  if (!data || !data.me) {
    return null;
  }
  if (data.me.businessAreas.edges.length < 1) {
    return <Redirect to='/access-denied' />;
  }
  return (
    <Redirect
      to={`/${data.me.businessAreas.edges[0].node.slug}/programs/all/list`}
    />
  );
}
