import * as Sentry from '@sentry/react';
import React from 'react';
import { Redirect, Route } from 'react-router-dom';
import { useBaseUrl } from '../../hooks/useBaseUrl';

export interface SentryRouteProps {
  children: React.ReactElement;
  path: string;
  label?: string;
  exact?: boolean;
}

export const SentryRoute = ({
  path,
  children,
  label,
  exact,
}: SentryRouteProps): React.ReactElement => {
  const { programId } = useBaseUrl();
  return (
    <>
      {programId ? (
        <>
          <Route exact={exact} path={path}>
            <Sentry.ErrorBoundary
              beforeCapture={(scope) => {
                scope.setTag('location', label || path);
              }}
            >
              {children}
            </Sentry.ErrorBoundary>
          </Route>
        </>
      ) : (
        <Redirect to='/' noThrow />
      )}
    </>
  );
};
