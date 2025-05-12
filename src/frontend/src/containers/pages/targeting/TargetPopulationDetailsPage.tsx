import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TargetPopulationCore } from '@components/targeting/TargetPopulationCore';
import TargetPopulationDetails from '@components/targeting/TargetPopulationDetails';
import {
  PaymentPlanBuildStatus,
  useBusinessAreaDataQuery,
  useTargetPopulationQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { TargetPopulationPageHeader } from '../headers/TargetPopulationPageHeader';
import withErrorBoundary from '@components/core/withErrorBoundary';

export const TargetPopulationDetailsPage = (): ReactElement => {
  const { id } = useParams();
  const { isStandardDctType, isSocialDctType } = useProgramContext();
  const permissions = usePermissions();
  const { data, loading, error, startPolling, stopPolling } =
    useTargetPopulationQuery({
      variables: { id },
      fetchPolicy: 'cache-and-network',
    });

  const { businessArea } = useBaseUrl();
  const { data: businessAreaData } = useBusinessAreaDataQuery({
    variables: { businessAreaSlug: businessArea },
  });

  const buildStatus = data?.paymentPlan?.buildStatus;
  useEffect(() => {
    if (
      [
        PaymentPlanBuildStatus.Building,
        PaymentPlanBuildStatus.Pending,
      ].includes(buildStatus)
    ) {
      startPolling(3000);
    } else {
      stopPolling();
    }
    return stopPolling;
  }, [buildStatus, startPolling, stopPolling]);

  if (loading && !data) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null || !businessAreaData) return null;

  const { paymentPlan } = data;

  const canDuplicate =
    hasPermissions(PERMISSIONS.TARGETING_DUPLICATE, permissions) &&
    Boolean(paymentPlan.targetingCriteria);

  return (
    <>
      <TargetPopulationPageHeader
        paymentPlan={paymentPlan}
        canEdit={hasPermissions(PERMISSIONS.TARGETING_UPDATE, permissions)}
        canRemove={hasPermissions(PERMISSIONS.TARGETING_REMOVE, permissions)}
        canDuplicate={canDuplicate}
        canLock={hasPermissions(PERMISSIONS.TARGETING_LOCK, permissions)}
        canUnlock={hasPermissions(PERMISSIONS.TARGETING_UNLOCK, permissions)}
        canSend={hasPermissions(PERMISSIONS.TARGETING_SEND, permissions)}
      />
      <TargetPopulationDetails targetPopulation={paymentPlan} />
      <TargetPopulationCore
        id={paymentPlan?.id}
        targetPopulation={paymentPlan}
        isStandardDctType={isStandardDctType}
        isSocialDctType={isSocialDctType}
        permissions={permissions}
        screenBeneficiary={businessAreaData?.businessArea?.screenBeneficiary}
      />
    </>
  );
};

export default withErrorBoundary(
  TargetPopulationDetailsPage,
  'TargetPopulationDetailsPage',
);
