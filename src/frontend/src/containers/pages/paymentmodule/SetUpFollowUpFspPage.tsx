import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { CreateSetUpFspHeader } from '@components/paymentmodule/CreateSetUpFsp/CreateSetUpFspHeader';
import { SetUpFspCore } from '@components/paymentmodule/CreateSetUpFsp/SetUpFspCore/SetUpFspCore';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { ReactElement } from 'react';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';

export const SetUpFollowUpFspPage = (): ReactElement => {
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
        chosenConfiguration: '',
      },
    ],
  };

  return (
    <>
      <CreateSetUpFspHeader baseUrl={baseUrl} permissions={permissions} />
      <SetUpFspCore permissions={permissions} initialValues={initialValues} />
    </>
  );
};

export default withErrorBoundary(SetUpFollowUpFspPage, 'SetUpFollowUpFspPage');
