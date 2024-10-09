import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { usePermissions } from '@hooks/usePermissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  PaymentPlanBackgroundActionStatus,
  PaymentPlanStatus,
  usePaymentPlanQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@core/LoadingComponent';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { isPermissionDeniedError } from '@utils/utils';
import { PermissionDenied } from '@core/PermissionDenied';
import { Box } from '@mui/material';
import { PaymentPlanDetailsHeader } from '@containers/pages/paymentmodule/ProgramCycle/PaymentPlanDetails/PaymentPlanDetailsHeader';
import { PaymentPlanDetails } from '@containers/pages/paymentmodule/ProgramCycle/PaymentPlanDetails/PaymentPlanDetails';
import { AcceptanceProcess } from '@components/paymentmodule/PaymentPlanDetails/AcceptanceProcess';
import { Entitlement } from '@components/paymentmodule/PaymentPlanDetails/Entitlement';
import { FspSection } from '@components/paymentmodule/PaymentPlanDetails/FspSection';
import { ExcludeSection } from '@components/paymentmodule/PaymentPlanDetails/ExcludeSection';
import { PaymentPlanDetailsResults } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults';
import { PaymentsTable } from '@containers/tables/paymentmodule/PaymentsTable';
import { ReconciliationSummary } from '@components/paymentmodule/PaymentPlanDetails/ReconciliationSummary';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import { SupportingDocumentsSection } from '@components/paymentmodule/PaymentPlanDetails/SupportingDocumentsSection/SupportingDocumentsSection';

export const PaymentPlanDetailsPage = (): React.ReactElement => {
  const { paymentPlanId } = useParams();
  const permissions = usePermissions();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data, loading, startPolling, stopPolling, error } =
    usePaymentPlanQuery({
      variables: {
        id: paymentPlanId,
      },
      fetchPolicy: 'network-only',
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
          <SupportingDocumentsSection paymentPlan={paymentPlan} />
          <PaymentPlanDetailsResults paymentPlan={paymentPlan} />
          <PaymentsTable
            businessArea={businessArea}
            paymentPlan={paymentPlan}
            permissions={permissions}
            canViewDetails
          />
          {shouldDisplayReconciliationSummary && (
            <ReconciliationSummary paymentPlan={paymentPlan} />
          )}
        </>
      )}
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={paymentPlan.id} />
      )}
    </Box>
  );
};
