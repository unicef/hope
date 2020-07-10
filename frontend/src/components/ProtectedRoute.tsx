import React from 'react';
import { Redirect, Route, useLocation } from 'react-router-dom';
import { isAuthenticated } from '../utils/utils';

export function ProtectedRoute({
  component: Component,
  ...rest
}): React.ReactElement {
  const authenticated = isAuthenticated();
  const location = useLocation();

  return (
    <Route
      {...rest}
      render={(props) => {
        if (authenticated) {
          return <Component {...props} />;
        }
        return (
          <Redirect to={`/login?next=${location.pathname}${location.search}`} />
        );
      }}
    />
  );
}
