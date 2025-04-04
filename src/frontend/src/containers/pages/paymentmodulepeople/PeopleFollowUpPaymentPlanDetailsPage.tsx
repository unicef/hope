import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { FollowUpPaymentPlanDetails } from '@components/paymentmodule/FollowUpPaymentPlanDetails/FollowUpPaymentPlanDetails';
import { FollowUpPaymentPlanDetailsHeader } from '@components/paymentmodule/FollowUpPaymentPlanDetails/FollowUpPaymentPlanDetailsHeader';
import { FspSection } from '@components/paymentmodule/PaymentPlanDetails/FspSection';
import { PaymentPlanDetailsResults } from '@components/paymentmodule/PaymentPlanDetails/PaymentPlanDetailsResults';
import { ReconciliationSummary } from '@components/paymentmodule/PaymentPlanDetails/ReconciliationSummary';
import { SupportingDocumentsSection } from '@components/paymentmodule/PaymentPlanDetails/SupportingDocumentsSection/SupportingDocumentsSection';
import { AcceptanceProcess } from '@components/paymentmodulepeople/PaymentPlanDetails/AcceptanceProcess';
import { Entitlement } from '@components/paymentmodulepeople/PaymentPlanDetails/Entitlement';
import { ExcludeSection } from '@components/paymentmodulepeople/PaymentPlanDetails/ExcludeSection';
import PaymentsTable from '@containers/tables/paymentmodule/PaymentsTable/PaymentsTable';
import {
  PaymentPlanBackgroundActionStatus,
  PaymentPlanStatus,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { error } from 'console';
import { ReactElement } from 'react';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';

export const PeopleFollowUpPaymentPlanDetailsPage = (): ReactElement => {
  const { paymentPlanId } = useParams();
  const permissions = usePermissions();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { data: paymentPlan, isLoading } = useQuery({
    queryKey: ['paymentPlan', businessArea, paymentPlanId, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansRetrieve({
        businessAreaSlug: businessArea,
        id: paymentPlanId,
        programSlug: programId,
      }),
    refetchInterval: () => {
      const { status, background_action_status } = paymentPlan;
      if (
        status === PaymentPlanStatus.Preparing ||
        (background_action_status !== null &&
          background_action_status !==
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
