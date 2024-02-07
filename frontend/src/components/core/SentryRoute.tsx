import * as Sentry from '@sentry/react';
import * as React from 'react';
import { Route } from 'react-router-dom';

export interface SentryRouteProps {
  children: React.ReactElement;
  path: string;
  label?: string;
  exact?: boolean;
}

export function SentryRoute({
  path,
  children,
  label,
  exact,
}: SentryRouteProps): React.ReactElement {
  return (
    <Route exact={exact} path={path}>
      <Sentry.ErrorBoundary
        beforeCapture={(scope) => {
          scope.setTag('location', label || path);
        }}
      >
        {children}
      </Sentry.ErrorBoundary>
    </Route>
  );
}
