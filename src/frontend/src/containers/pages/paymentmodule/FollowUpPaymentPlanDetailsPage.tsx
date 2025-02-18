import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { FollowUpPaymentPlanDetails } from '@components/paymentmodule/FollowUpPaymentPlanDetails/FollowUpPaymentPlanDetails';
import { FollowUpPaymentPlanDetailsHeader } from '@components/paymentmodule/FollowUpPaymentPlanDetails/FollowUpPaymentPlanDetailsHeader';
import { AcceptanceProcess } from '@components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/AcceptanceProcess';
import { Entitlement } from '@components/paymentmodule/PaymentPlanDetails/Entitlement/Entitlement';
import { ExcludeSection } from '@components/paymentmodule/PaymentPlanDetails/ExcludeSection';
import { FspSection } from '@components/paymentmodule/PaymentPlanDetails/FspSection';
import { PaymentPlanDetailsResults } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults';
import { ReconciliationSummary } from '@components/paymentmodule/PaymentPlanDetails/ReconciliationSummary';
import { SupportingDocumentsSection } from '@components/paymentmodule/PaymentPlanDetails/SupportingDocumentsSection/SupportingDocumentsSection';
import { PaymentPlanStatus, usePaymentPlanQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import PaymentsTable from '@containers/tables/paymentmodule/PaymentsTable/PaymentsTable';

export function FollowUpPaymentPlanDetailsPage(): ReactElement {
  const { paymentPlanId } = useParams();
  const permissions = usePermissions();
  const { baseUrl, businessArea } = useBaseUrl();
  const { data, loading, startPolling, stopPolling, error } =
    usePaymentPlanQuery({
      variables: {
        id: paymentPlanId,
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
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={paymentPlan.id} />
      )}
    </>
  );
}
export default withErrorBoundary(
  FollowUpPaymentPlanDetailsPage,
  'FollowUpPaymentPlanDetailsPage',
);
