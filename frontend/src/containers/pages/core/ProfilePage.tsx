import React, { useEffect } from 'react';
import { Redirect, useLocation } from 'react-router-dom';
import { useLoggedCheckerQuery } from '../../../__generated__/graphql';
import { LOGIN_URL } from '../../../config';

export function ProfilePage(): React.ReactElement {
  const location = useLocation();
  const { error } = useLoggedCheckerQuery({ fetchPolicy: 'network-only' });
  useEffect(() => {
    if (error) {
      window.location.replace(
        `${LOGIN_URL}?next=${location.pathname}${location.search}`,
      );
    }
  });
  const params = new URLSearchParams(location.search);
  const next = params.get('next') ? params.get('next') : '/';
  if (error) {
    return null;
  }
  return <Redirect to={next} />;
}
