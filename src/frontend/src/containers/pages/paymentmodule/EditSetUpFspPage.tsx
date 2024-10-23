import * as React from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { SetUpFspCore } from '@components/paymentmodule/CreateSetUpFsp/SetUpFspCore/SetUpFspCore';
import { EditSetUpFspHeader } from '@components/paymentmodule/EditSetUpFsp/EditSetUpFspHeader';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { usePaymentPlanQuery } from '@generated/graphql';
import { UniversalErrorBoundary } from '@components/core/UniversalErrorBoundary';

export function EditSetUpFspPage(): React.ReactElement {
  const { paymentPlanId } = useParams();
  const location = useLocation();

  const { data: paymentPlanData, loading: paymentPlanLoading } =
    usePaymentPlanQuery({
      variables: {
        id: paymentPlanId,
      },
      fetchPolicy: 'cache-and-network',
    });

  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP, permissions))
    return <PermissionDenied />;
  if (!paymentPlanData) return null;
  if (paymentPlanLoading) return <LoadingComponent />;

  const mappedInitialDeliveryMechanisms =
    paymentPlanData.paymentPlan.deliveryMechanisms.map((el) => ({
      deliveryMechanism: el.code,
      fsp: el.fsp?.id || '',
      chosenConfiguration: el.chosenConfiguration || '',
    }));

  const initialValues = {
    deliveryMechanisms: mappedInitialDeliveryMechanisms,
  };

  return (
    <UniversalErrorBoundary
      location={location}
      beforeCapture={(scope) => {
        scope.setTag('location', location.pathname);
        scope.setTag('component', 'EditSetUpFspPage.tsx');
      }}
      componentName="EditSetUpFspPage"
    >
      <EditSetUpFspHeader permissions={permissions} />
      <SetUpFspCore permissions={permissions} initialValues={initialValues} />
    </UniversalErrorBoundary>
  );
}
