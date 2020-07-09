import React from 'react';
import { Redirect, Route } from 'react-router-dom';
import { isAuthenticated } from '../utils/utils';

export function ProtectedRoute({
  component: Component,
  ...rest
}): React.ReactElement {
  const authenticated = isAuthenticated();
  return (
    <Route
      {...rest}
      render={(props) => {
        if (authenticated) {
          return <Component {...props} />;
        }
        return (
          <Redirect
            to={{
              pathname: '/login',
              state: { from: props.location },
            }}
          />
        );
      }}
    />
  );
}
