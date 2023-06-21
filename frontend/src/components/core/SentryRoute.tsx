import * as Sentry from '@sentry/react';
import React from 'react';
import { Redirect, Route } from 'react-router-dom';

export interface SentryRouteProps {
  children: React.ReactElement;
  path: string;
  label?: string;
  exact?: boolean;
  shouldRender?: boolean;
}

export const SentryRoute = ({
  path,
  children,
  label,
  exact,
  shouldRender = true,
}: SentryRouteProps): React.ReactElement => (
  <>
    {shouldRender ? (
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
