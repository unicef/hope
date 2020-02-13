import { Redirect } from 'react-router-dom';
import React from 'react';
import { useMeQuery } from '../__generated__/graphql';

export function DefaultRoute(): React.ReactElement {
  const { data } = useMeQuery();
  if (!data || !data.me) {
    return null;
  }
  if (data.me.businessAreas.edges.length < 1) {
    return <div>You dont have any business area asigned to your account</div>;
  }
  return <Redirect to={`/${data.me.businessAreas.edges[0].node.slug}/`} />;
}
