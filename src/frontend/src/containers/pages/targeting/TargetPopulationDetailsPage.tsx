import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { TargetPopulationCore } from '@components/targeting/TargetPopulationCore';
import TargetPopulationDetails from '@components/targeting/TargetPopulationDetails';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement } from 'react';
import { useParams } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { TargetPopulationPageHeader } from '../headers/TargetPopulationPageHeader';

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

  const {
    data: paymentPlan,
    isLoading: loading,
    error,
  } = useQuery<TargetPopulationDetail>({
    queryKey: ['targetPopulation', businessArea, id, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsRetrieve({
        businessAreaSlug: businessArea,
        id: id,
        programSlug: programId,
      }),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (['BUILDING', 'PENDING'].includes(data?.backgroundActionStatus)) {
        return 3000;
      }

      return false;
    },
    refetchIntervalInBackground: true,
  });

  if (loading && !paymentPlan) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null || !businessAreaData) return null;

  const { paymentPlan } = data;
    const { data: programData } = useProgramQuery({
    variables: { id: programId },
  });

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
        screenBeneficiary={programData?.program?.screenBeneficiary}
      />
    </>
  );
};

export default withErrorBoundary(
  TargetPopulationDetailsPage,
  'TargetPopulationDetailsPage',
);
