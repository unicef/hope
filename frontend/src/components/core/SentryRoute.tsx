import * as Sentry from '@sentry/react';
import * as React from 'react';
import { Route } from 'react-router-dom';

export interface SentryRouteProps {
  element: React.ReactElement;
  path: string;
  label?: string;
}

export const SentryRoute = ({
  path,
  element,
  label,
}: SentryRouteProps): React.ReactElement => {
  return (
    <Route
      path={path}
      element={
        <Sentry.ErrorBoundary
          beforeCapture={(scope) => {
            scope.setTag('location', label || path);
          }}
        >
          {element}
        </Sentry.ErrorBoundary>
      }
    />
  );
};
