import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  PaymentPlanStatus,
  usePaymentPlanQuery,
} from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { FollowUpPaymentPlanDetails } from '../../../components/paymentmodule/FollowUpPaymentPlanDetails/FollowUpPaymentPlanDetails';
import { FollowUpPaymentPlanDetailsHeader } from '../../../components/paymentmodule/FollowUpPaymentPlanDetails/FollowUpPaymentPlanDetailsHeader';
import { AcceptanceProcess } from '../../../components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/AcceptanceProcess';
import { Entitlement } from '../../../components/paymentmodule/PaymentPlanDetails/Entitlement/Entitlement';
import { FspSection } from '../../../components/paymentmodule/PaymentPlanDetails/FspSection';
import { PaymentPlanDetailsResults } from '../../../components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults';
import { ReconciliationSummary } from '../../../components/paymentmodule/PaymentPlanDetails/ReconciliationSummary';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import { PaymentsTable } from '../../tables/paymentmodule/PaymentsTable';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { ExcludeSection } from '../../../components/paymentmodule/PaymentPlanDetails/ExcludeSection';
import { useBaseUrl } from '../../../hooks/useBaseUrl';

export const FollowUpPaymentPlanDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const { baseUrl, businessArea } = useBaseUrl();
  const {
    data,
    loading,
    startPolling,
    stopPolling,
    error,
  } = usePaymentPlanQuery({
    variables: {
      id,
    },
    fetchPolicy: 'cache-and-network',
  });

  const status = data?.paymentPlan?.status;

  useEffect(() => {
    if (PaymentPlanStatus.Preparing === status) {
      startPolling(3000);
    } else {
      stopPolling();
    }
    return stopPolling;
  }, [status, startPolling, stopPolling]);

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
    <>
      <FollowUpPaymentPlanDetailsHeader
        paymentPlan={paymentPlan}
        baseUrl={baseUrl}
        permissions={permissions}
      />
      <FollowUpPaymentPlanDetails baseUrl={baseUrl} paymentPlan={paymentPlan} />
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
  );
};
