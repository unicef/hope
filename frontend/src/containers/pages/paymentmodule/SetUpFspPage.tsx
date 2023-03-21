import React from 'react';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { CreateSetUpFspHeader } from '../../../components/paymentmodule/CreateSetUpFsp/CreateSetUpFspHeader';
import { SetUpFspCore } from '../../../components/paymentmodule/CreateSetUpFsp/SetUpFspCore/SetUpFspCore';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';

export const SetUpFspPage = (): React.ReactElement => {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (
    !hasPermissions(
      PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP,
      permissions,
    )
  )
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
      <CreateSetUpFspHeader
        businessArea={businessArea}
        permissions={permissions}
      />
      <SetUpFspCore
        businessArea={businessArea}
        permissions={permissions}
        initialValues={initialValues}
      />
    </>
  );
};
