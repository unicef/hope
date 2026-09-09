import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { TargetPopulationCore } from '@components/targeting/TargetPopulationCore';
import TargetPopulationDetails from '@components/targeting/TargetPopulationDetails';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import type { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { isPermissionDeniedError } from '@utils/utils';
import type { ReactElement } from 'react';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { TargetPopulationPageHeader } from '../headers/TargetPopulationPageHeader';

export const TargetPopulationDetailsPage = (): ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();

  const { businessAreaSlug, programCode } = useBaseUrl();
  const {
    data: paymentPlan,
    isLoading: loading,
    error,
  } = useQuery<TargetPopulationDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsTargetPopulationsRetrieve,
      {
        businessAreaSlug: businessAreaSlug,
        id: id,
        programCode,
      },
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsRetrieve({
        businessAreaSlug: businessAreaSlug,
        id: id,
        programCode,
      }),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (['BUILDING', 'PENDING'].includes(data?.backgroundActionStatus)) {
        return 3000;
      }

      return false;
    },
  });

  if (loading && !paymentPlan) return <LoadingComponent />;

  if (isPermissionDeniedError(error))
    return <PermissionDenied permission={PERMISSIONS.TARGETING_VIEW_DETAILS} />;

  const canDuplicate =
    hasPermissions(PERMISSIONS.TARGETING_DUPLICATE, permissions) &&
    Boolean(paymentPlan?.rules);

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
        permissions={permissions}
        screenBeneficiary={paymentPlan?.program?.screenBeneficiary}
      />
    </>
  );
};

export default withErrorBoundary(
  TargetPopulationDetailsPage,
  'TargetPopulationDetailsPage',
);
