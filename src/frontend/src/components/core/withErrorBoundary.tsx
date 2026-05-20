import { UniversalErrorBoundary } from '@components/core/UniversalErrorBoundary';

const withErrorBoundary = (Component, componentName) => {
  const WrappedComponent = (props) => {
    return (
      <UniversalErrorBoundary
        beforeCapture={(scope) => {
          scope.setTag('location', window.location.pathname);
          scope.setTag('component', componentName);
        }}
        componentName={componentName}
      >
        <Component {...props} />
      </UniversalErrorBoundary>
    );
  };

  WrappedComponent.displayName = `WithErrorBoundary(${componentName})`;

  return WrappedComponent;
};

export default withErrorBoundary;
