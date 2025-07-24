import withErrorBoundary from '@components/core/withErrorBoundary';
import { FspSection } from '@components/paymentmodule/PaymentPlanDetails/FspSection';
import { PaymentPlanDetailsResults } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults';
import { ReconciliationSummary } from '@components/paymentmodule/PaymentPlanDetails/ReconciliationSummary';
import { SupportingDocumentsSection } from '@components/paymentmodule/PaymentPlanDetails/SupportingDocumentsSection/SupportingDocumentsSection';
import { PaymentPlanDetails } from '@containers/pages/paymentmodule/ProgramCycle/PaymentPlanDetails/PaymentPlanDetails';
import { PaymentPlanDetailsHeader } from '@containers/pages/paymentmodule/ProgramCycle/PaymentPlanDetails/PaymentPlanDetailsHeader';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import { LoadingComponent } from '@core/LoadingComponent';
import { PermissionDenied } from '@core/PermissionDenied';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { PaymentPlanBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanBackgroundActionStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement } from 'react';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import PaymentsTable from '@containers/tables/paymentmodule/PaymentsTable/PaymentsTable';
import { AcceptanceProcess } from '@components/paymentmodulepeople/PaymentPlanDetails/AcceptanceProcess';
import { Entitlement } from '@components/paymentmodulepeople/PaymentPlanDetails/Entitlement';
import ExcludeSection from '@components/paymentmodule/PaymentPlanDetails/ExcludeSection/ExcludeSection';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import FundsCommitmentSection from '@components/paymentmodule/PaymentPlanDetails/FundsCommitment/FundsCommitmentSection';

const PaymentPlanDetailsPage = (): ReactElement => {
  const { paymentPlanId } = useParams();
  const permissions = usePermissions();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const {
    data: paymentPlan,
    isLoading,
    error,
  } = useQuery<PaymentPlanDetail>({
    queryKey: ['paymentPlan', businessArea, paymentPlanId, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansRetrieve({
        businessAreaSlug: businessArea,
        id: paymentPlanId,
        programSlug: programId,
      }),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (
        data?.status === PaymentPlanStatusEnum.PREPARING ||
        (data?.backgroundActionStatus !== null &&
          data?.backgroundActionStatus !==
            PaymentPlanBackgroundActionStatusEnum.EXCLUDE_BENEFICIARIES_ERROR)
      ) {
        return 3000;
      }

      return false;
    },
    refetchIntervalInBackground: true,
  });

  if (isLoading) return <LoadingComponent />;
  if (permissions === null || !paymentPlan) return null;

  if (
    !hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions) ||
    isPermissionDeniedError(error)
  )
    return <PermissionDenied />;
  if (!paymentPlan) return null;

  const { status } = paymentPlan;

  const shouldDisplayEntitlement =
    status !== PaymentPlanStatusEnum.OPEN &&
    status !== PaymentPlanStatusEnum.ACCEPTED;

  const shouldDisplayFsp = status !== PaymentPlanStatusEnum.OPEN;
  const shouldDisplayReconciliationSummary =
    status === PaymentPlanStatusEnum.ACCEPTED ||
    status === PaymentPlanStatusEnum.FINISHED;

  const shouldDisplayFundsCommitment =
    status === PaymentPlanStatusEnum.IN_REVIEW ||
    status === PaymentPlanStatusEnum.ACCEPTED ||
    status === PaymentPlanStatusEnum.FINISHED;

  return (
    <Box display="flex" flexDirection="column">
      <PaymentPlanDetailsHeader
        paymentPlan={paymentPlan}
        permissions={permissions}
      />
      <PaymentPlanDetails baseUrl={baseUrl} paymentPlan={paymentPlan} />
      {status !== PaymentPlanStatusEnum.PREPARING && (
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
        <UniversalActivityLogTable objectId={paymentPlan?.id} />
      )}
    </Box>
  );
};

export default withErrorBoundary(
  PaymentPlanDetailsPage,
  'PaymentPlanDetailsPage',
);
