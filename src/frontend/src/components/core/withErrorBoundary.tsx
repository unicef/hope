import { UniversalErrorBoundary } from '@components/core/UniversalErrorBoundary';
import { useLocation } from 'react-router-dom';

const withErrorBoundary = (Component, componentName) => {
  const WrappedComponent = (props) => {
    const location = useLocation();

    return (
      <UniversalErrorBoundary
        location={location}
        beforeCapture={(scope) => {
          scope.setTag('location', location.pathname);
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
