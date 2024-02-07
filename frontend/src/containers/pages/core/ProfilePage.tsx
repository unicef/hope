import * as React from 'react';
import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useLoggedCheckerQuery } from '../../../__generated__/graphql';
import { LOGIN_URL } from '../../../config';

export const ProfilePage = (): React.ReactElement | null => {
  const location = useLocation();
  const navigate = useNavigate();
  const { error } = useLoggedCheckerQuery({ fetchPolicy: 'network-only' });
  const params = new URLSearchParams(location.search);
  const next = params.get('next') ? params.get('next') : '/';

  useEffect(() => {
    if (error) {
      window.location.replace(
        `${LOGIN_URL}?next=${location.pathname}${location.search}`,
      );
    }
    if (next?.startsWith('/api/')) {
      window.location.replace(next);
    }
  }, [error, location, next]);

  useEffect(() => {
    if (!error && next && !next.startsWith('/api/')) {
      navigate(next);
    }
  }, [error, navigate, next]);

  return null;
};
