import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TargetPopulationCore } from '../../../components/targeting/TargetPopulationCore';
import { TargetPopulationDetails } from '../../../components/targeting/TargetPopulationDetails';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useLazyInterval } from '../../../hooks/useInterval';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import {
  TargetPopulationBuildStatus,
  useTargetPopulationQuery,
} from '../../../__generated__/graphql';
import { TargetPopulationPageHeader } from '../headers/TargetPopulationPageHeader';

export const TargetPopulationDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading, error, refetch } = useTargetPopulationQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const [
    startPollingTargetPopulation,
    stopPollingTargetPopulation,
  ] = useLazyInterval(() => refetch(), 3000);
  const buildStatus = data?.targetPopulation?.buildStatus;
  useEffect(() => {
    if (
      [
        TargetPopulationBuildStatus.Building,
        TargetPopulationBuildStatus.Pending,
      ].includes(buildStatus)
    ) {
      startPollingTargetPopulation();
    } else {
      stopPollingTargetPopulation();
    }
    return stopPollingTargetPopulation;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [buildStatus]);

  if (loading && !data) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null) return null;

  const { targetPopulation } = data;

  const canDuplicate =
    hasPermissions(PERMISSIONS.TARGETING_DUPLICATE, permissions) &&
    Boolean(targetPopulation.targetingCriteria);

  return (
    <>
      <TargetPopulationPageHeader
        targetPopulation={targetPopulation}
        canEdit={hasPermissions(PERMISSIONS.TARGETING_UPDATE, permissions)}
        canRemove={hasPermissions(PERMISSIONS.TARGETING_REMOVE, permissions)}
        canDuplicate={canDuplicate}
        canLock={hasPermissions(PERMISSIONS.TARGETING_LOCK, permissions)}
        canUnlock={hasPermissions(PERMISSIONS.TARGETING_UNLOCK, permissions)}
        canSend={hasPermissions(PERMISSIONS.TARGETING_SEND, permissions)}
      />
      <TargetPopulationDetails targetPopulation={targetPopulation} />
      <TargetPopulationCore
        id={targetPopulation.id}
        targetPopulation={targetPopulation}
        permissions={permissions}
      />
    </>
  );
};
