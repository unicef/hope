import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { FspSection } from '@components/paymentmodule/PaymentPlanDetails/FspSection';
import FundsCommitmentSection from '@components/paymentmodule/PaymentPlanDetails/FundsCommitment/FundsCommitmentSection';
import { PaymentPlanDetailsHeader } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsHeader';
import { ReconciliationSummary } from '@components/paymentmodule/PaymentPlanDetails/ReconciliationSummary';
import { SupportingDocumentsSection } from '@components/paymentmodule/PaymentPlanDetails/SupportingDocumentsSection/SupportingDocumentsSection';
import { AcceptanceProcess } from '@components/paymentmodulepeople/PaymentPlanDetails/AcceptanceProcess';
import { Entitlement } from '@components/paymentmodulepeople/PaymentPlanDetails/Entitlement';
import { ExcludeSection } from '@components/paymentmodulepeople/PaymentPlanDetails/ExcludeSection';
import { PaymentPlanDetails } from '@components/paymentmodulepeople/PaymentPlanDetails/PaymentPlanDetails';
import { PeoplePaymentPlanDetailsResults } from '@components/paymentmodulepeople/PaymentPlanDetails/PeoplePaymentPlanDetailsResults';
import PeoplePaymentsTable from '@containers/tables/paymentmodulePeople/PeoplePaymentsTable/PeoplePaymentsTable';
import {
  PaymentPlanBackgroundActionStatus,
  PaymentPlanStatus,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement } from 'react';
import { useParams } from 'react-router-dom';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';

export const PeoplePaymentPlanDetailsPage = (): ReactElement => {
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
        data?.status === PaymentPlanStatus.Preparing ||
        (data?.backgroundActionStatus !== null &&
          data?.backgroundActionStatus !==
            PaymentPlanBackgroundActionStatus.ExcludeBeneficiariesError)
      ) {
        return 3000;
      }

      return false;
    },
    refetchIntervalInBackground: true,
  });

  if (isLoading && !paymentPlan) return <LoadingComponent />;
  if (permissions === null || !paymentPlan) return null;

  if (
    !hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions) ||
    isPermissionDeniedError(error)
  )
    return <PermissionDenied />;

  const { status } = paymentPlan;

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
