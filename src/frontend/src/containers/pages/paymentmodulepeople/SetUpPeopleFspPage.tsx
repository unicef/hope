import * as React from 'react';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { CreateSetUpFspHeader } from '@components/paymentmodule/CreateSetUpFsp/CreateSetUpFspHeader';
import { SetUpFspCore } from '@components/paymentmodule/CreateSetUpFsp/SetUpFspCore/SetUpFspCore';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { UniversalErrorBoundary } from '@components/core/UniversalErrorBoundary';
import { useLocation } from 'react-router-dom';

export const SetUpPeopleFspPage = (): React.ReactElement => {
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP, permissions))
    return <PermissionDenied />;

  const initialValues = {
    deliveryMechanisms: [
      {
        deliveryMechanism: '',
        fsp: '',
        chosenConfiguration: '',
      },
    ],
  };

  return (
    <UniversalErrorBoundary
      location={location}
      beforeCapture={(scope) => {
        scope.setTag('location', location.pathname);
        scope.setTag('component', 'SetUpPeopleFspPage.tsx');
      }}
      componentName="SetUpPeopleFspPage"
    >
      <>
        <CreateSetUpFspHeader baseUrl={baseUrl} permissions={permissions} />
        <SetUpFspCore permissions={permissions} initialValues={initialValues} />
      </>
    </UniversalErrorBoundary>
  );
};
