import React, { useEffect } from 'react';
import { Redirect, useLocation } from 'react-router-dom';
import { useMeQuery } from '../../__generated__/graphql';
import { setAuthenticated } from '../../utils/utils';
import { LOGIN_URL } from '../../config';

export function ProfilePage(): React.ReactElement {
  const location = useLocation();
  const { error } = useMeQuery();
  useEffect(() => {
    if (error) {
      window.location.replace(
        `${LOGIN_URL}?next=${location.pathname}${location.search}`,
      );
    }
  });
  const params = new URLSearchParams(location.search);
  const next = params.get('next');
  if (error) {
    return null;
  }
  setAuthenticated(true);
  return <Redirect to={next} />;
}
