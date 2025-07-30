import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { FollowUpPaymentPlanDetails } from '@components/paymentmodule/FollowUpPaymentPlanDetails/FollowUpPaymentPlanDetails';
import { FollowUpPaymentPlanDetailsHeader } from '@components/paymentmodule/FollowUpPaymentPlanDetails/FollowUpPaymentPlanDetailsHeader';
import { PaymentPlanDetailsResults } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults';
import { ReconciliationSummary } from '@components/paymentmodule/PaymentPlanDetails/ReconciliationSummary';
import { SupportingDocumentsSection } from '@components/paymentmodule/PaymentPlanDetails/SupportingDocumentsSection/SupportingDocumentsSection';
import { AcceptanceProcess } from '@components/paymentmodulepeople/PaymentPlanDetails/AcceptanceProcess';
import { Entitlement } from '@components/paymentmodulepeople/PaymentPlanDetails/Entitlement';
import { ExcludeSection } from '@components/paymentmodulepeople/PaymentPlanDetails/ExcludeSection';
import PaymentsTable from '@containers/tables/paymentmodule/PaymentsTable/PaymentsTable';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { PaymentPlanBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanBackgroundActionStatusEnum';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement } from 'react';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

export const PeopleFollowUpPaymentPlanDetailsPage = (): ReactElement => {
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

  if (isLoading && !paymentPlan) return <LoadingComponent />;
  if (permissions === null || !paymentPlan) return null;

  if (
    !hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions) ||
    isPermissionDeniedError(error)
  )
    return <PermissionDenied />;

  const { status } = paymentPlan;

  const shouldDisplayEntitlement =
    status !== PaymentPlanStatusEnum.OPEN &&
    status !== PaymentPlanStatusEnum.ACCEPTED;

  const shouldDisplayFsp = status !== PaymentPlanStatusEnum.OPEN;
  const shouldDisplayReconciliationSummary =
    status === PaymentPlanStatusEnum.ACCEPTED ||
    status === PaymentPlanStatusEnum.FINISHED;

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
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={paymentPlan.id} />
      )}
    </>
  );
};
export default withErrorBoundary(
  PeopleFollowUpPaymentPlanDetailsPage,
  'PeopleFollowUpPaymentPlanDetailsPage',
);
