import { FC, ReactNode } from 'react';
import { ErrorBoundary, ErrorBoundaryProps } from '@sentry/react';
import { SomethingWentWrong } from '@containers/pages/somethingWentWrong/SomethingWentWrong';
import { PageNotFound } from '@containers/pages/404/PageNotFound';
import { NotFoundError } from '@utils/errors';

interface UniversalErrorBoundaryProps extends ErrorBoundaryProps {
  location?: { pathname: string };
  children: ReactNode;
  componentName: string;
}

export const UniversalErrorBoundary: FC<UniversalErrorBoundaryProps> = ({
  location,
  children,
  componentName,
  ...rest
}) => {
  const pathname = location?.pathname ?? window.location.pathname;
  return (
    <ErrorBoundary
      fallback={({ error: err }) =>
        err instanceof NotFoundError ? (
          <PageNotFound />
        ) : (
          <SomethingWentWrong
            pathname={pathname}
            errorMessage={(err as Error).message}
            component={componentName}
          />
        )
      }
      {...rest}
    >
      {children}
    </ErrorBoundary>
  );
};
