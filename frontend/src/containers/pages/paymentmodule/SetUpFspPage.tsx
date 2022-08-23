import React, { useState } from 'react';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { CreateSetUpFspHeader } from '../../../components/paymentmodule/CreateSetUpFsp/CreateSetUpFspHeader';
import { SetUpFspCore } from '../../../components/paymentmodule/CreateSetUpFsp/SetUpFspCore/SetUpFspCore';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';

export const SetUpFspPage = (): React.ReactElement => {
  const [deliveryMechanismsForQuery, setDeliveryMechanismsForQuery] = useState(
    [],
  );

  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (
    !hasPermissions(PERMISSIONS.FINANCIAL_SERVICE_PROVIDER_CREATE, permissions)
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
        deliveryMechanismsForQuery={deliveryMechanismsForQuery}
        setDeliveryMechanismsForQuery={setDeliveryMechanismsForQuery}
      />
    </>
  );
};
