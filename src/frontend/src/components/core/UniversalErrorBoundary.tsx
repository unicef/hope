import React from 'react';
import { ErrorBoundary, ErrorBoundaryProps } from '@sentry/react';
import { SomethingWentWrong } from '@containers/pages/somethingWentWrong/SomethingWentWrong';

interface UniversalErrorBoundaryProps extends ErrorBoundaryProps {
  location: { pathname: string };
  children: React.ReactNode;
  componentName: string;
}

export const UniversalErrorBoundary: React.FC<UniversalErrorBoundaryProps> = ({
  location,
  children,
  componentName,
  ...rest
}) => {
  return (
    <ErrorBoundary
      fallback={({ error: err }) => (
        <SomethingWentWrong
          pathname={location.pathname}
          errorMessage={err.message}
          component={componentName}
        />
      )}
      {...rest}
    >
      {children}
    </ErrorBoundary>
  );
};
