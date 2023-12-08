import React from 'react';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { CreateSetUpFspHeader } from '../../../components/paymentmodule/CreateSetUpFsp/CreateSetUpFspHeader';
import { SetUpFspCore } from '../../../components/paymentmodule/CreateSetUpFsp/SetUpFspCore/SetUpFspCore';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

export const SetUpFspPage = (): React.ReactElement => {
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP, permissions))
    return <PermissionDenied />;

  const initialValues = {
    deliveryMechanisms: [
      {
        deliveryMechanism: '',
        fsp: '',
      },
    ],
  };

  return (
    <>
      <CreateSetUpFspHeader baseUrl={baseUrl} permissions={permissions} />
      <SetUpFspCore
        baseUrl={baseUrl}
        permissions={permissions}
        initialValues={initialValues}
      />
    </>
  );
};
