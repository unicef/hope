import { Box } from '@mui/material';
import * as React from 'react';
import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  PaymentPlanBackgroundActionStatus,
  PaymentPlanStatus,
  usePaymentPlanQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { AcceptanceProcess } from '@components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/AcceptanceProcess';
import { Entitlement } from '@components/paymentmodule/PaymentPlanDetails/Entitlement/Entitlement';
import { ExcludeSection } from '@components/paymentmodule/PaymentPlanDetails/ExcludeSection';
import { FspSection } from '@components/paymentmodule/PaymentPlanDetails/FspSection';
import { PaymentPlanDetails } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetails';
import { PaymentPlanDetailsHeader } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader';
import { PaymentPlanDetailsResults } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults';
import { ReconciliationSummary } from '@components/paymentmodule/PaymentPlanDetails/ReconciliationSummary';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { PaymentsTable } from '../../tables/paymentmodule/PaymentsTable';

export function PaymentPlanDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const permissions = usePermissions();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data, loading, startPolling, stopPolling, error } =
    usePaymentPlanQuery({
      variables: {
        id,
      },
      fetchPolicy: 'cache-and-network',
    });

  const status = data?.paymentPlan?.status;
  const backgroundActionStatus = data?.paymentPlan?.backgroundActionStatus;

  useEffect(() => {
    if (
      PaymentPlanStatus.Preparing === status ||
      (backgroundActionStatus !== null &&
        backgroundActionStatus !==
          PaymentPlanBackgroundActionStatus.ExcludeBeneficiariesError)
    ) {
      startPolling(3000);
    } else {
      stopPolling();
    }
    return stopPolling;
  }, [status, backgroundActionStatus, startPolling, stopPolling]);

  if (loading && !data) return <LoadingComponent />;
  if (permissions === null || !data) return null;

  if (
    !hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions) ||
    isPermissionDeniedError(error)
  )
    return <PermissionDenied />;

  const shouldDisplayEntitlement =
    status !== PaymentPlanStatus.Open && status !== PaymentPlanStatus.Accepted;

  const shouldDisplayFsp = status !== PaymentPlanStatus.Open;
  const shouldDisplayReconciliationSummary =
    status === PaymentPlanStatus.Accepted ||
    status === PaymentPlanStatus.Finished;

  const { paymentPlan } = data;

  return (
    <Box display="flex" flexDirection="column">
      <PaymentPlanDetailsHeader
        paymentPlan={paymentPlan}
        baseUrl={baseUrl}
        permissions={permissions}
      />
      <PaymentPlanDetails baseUrl={baseUrl} paymentPlan={paymentPlan} />
      {status !== PaymentPlanStatus.Preparing && (
        <>
          <AcceptanceProcess paymentPlan={paymentPlan} />
          {shouldDisplayEntitlement && (
            <Entitlement paymentPlan={paymentPlan} permissions={permissions} />
          )}
          {shouldDisplayFsp && (
            <FspSection baseUrl={baseUrl} paymentPlan={paymentPlan} />
          )}
          <ExcludeSection paymentPlan={paymentPlan} />
          <PaymentPlanDetailsResults paymentPlan={paymentPlan} />
          <PaymentsTable
            baseUrl={baseUrl}
            businessArea={businessArea}
            paymentPlan={paymentPlan}
            permissions={permissions}
            canViewDetails
          />
          {shouldDisplayReconciliationSummary && (
            <ReconciliationSummary paymentPlan={paymentPlan} />
          )}
          {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
            <UniversalActivityLogTable objectId={paymentPlan.id} />
          )}
        </>
      )}
    </Box>
  );
}
