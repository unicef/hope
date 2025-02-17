import  { FC, ReactNode } from 'react';
import { ErrorBoundary, ErrorBoundaryProps } from '@sentry/react';
import { SomethingWentWrong } from '@containers/pages/somethingWentWrong/SomethingWentWrong';

interface UniversalErrorBoundaryProps extends ErrorBoundaryProps {
  location: { pathname: string };
  children: ReactNode;
  componentName: string;
}

export const UniversalErrorBoundary: FC<UniversalErrorBoundaryProps> = ({
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
          errorMessage={(err as Error).message}
          component={componentName}
        />
      )}
      {...rest}
    >
      {children}
    </ErrorBoundary>
  );
};
