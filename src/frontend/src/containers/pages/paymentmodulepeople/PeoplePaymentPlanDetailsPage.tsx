import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { FspSection } from '@components/paymentmodule/PaymentPlanDetails/FspSection';
import { PaymentPlanDetailsHeader } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader';
import { ReconciliationSummary } from '@components/paymentmodule/PaymentPlanDetails/ReconciliationSummary';
import { SupportingDocumentsSection } from '@components/paymentmodule/PaymentPlanDetails/SupportingDocumentsSection/SupportingDocumentsSection';
import { ExcludeSection } from '@components/paymentmodulepeople/PaymentPlanDetails/ExcludeSection';
import { PeoplePaymentPlanDetailsResults } from '@components/paymentmodulepeople/PaymentPlanDetails/PeoplePaymentPlanDetailsResults';
import {
  PaymentPlanBackgroundActionStatus,
  PaymentPlanStatus,
  usePaymentPlanQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import PeoplePaymentsTable from '@containers/tables/paymentmodulePeople/PeoplePaymentsTable/PeoplePaymentsTable';
import { AcceptanceProcess } from '@components/paymentmodulepeople/PaymentPlanDetails/AcceptanceProcess';
import { PaymentPlanDetails } from '@components/paymentmodulepeople/PaymentPlanDetails/PaymentPlanDetails';
import { Entitlement } from '@components/paymentmodulepeople/PaymentPlanDetails/Entitlement';
import FundsCommitmentSection from '@components/paymentmodule/PaymentPlanDetails/FundsCommitment/FundsCommitmentSection';

export const PeoplePaymentPlanDetailsPage = (): ReactElement => {
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

  const shouldDisplayFundsCommitment =
    status === PaymentPlanStatus.InReview ||
    status === PaymentPlanStatus.Accepted ||
    status === PaymentPlanStatus.Finished;

  const { paymentPlan } = data;
  if (!paymentPlan) return null;

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
          {shouldDisplayFundsCommitment && (
            <FundsCommitmentSection paymentPlan={paymentPlan} />
          )}
          {shouldDisplayEntitlement && (
            <Entitlement paymentPlan={paymentPlan} permissions={permissions} />
          )}
          {shouldDisplayFsp && <FspSection paymentPlan={paymentPlan} />}
          <ExcludeSection paymentPlan={paymentPlan} />
          <SupportingDocumentsSection paymentPlan={paymentPlan} />
          <PeoplePaymentPlanDetailsResults paymentPlan={paymentPlan} />
          <PeoplePaymentsTable
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
};
export default withErrorBoundary(
  PeoplePaymentPlanDetailsPage,
  'PeoplePaymentPlanDetailsPage',
);
