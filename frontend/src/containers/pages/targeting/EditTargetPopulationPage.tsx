import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { EditTargetPopulation } from '../../../components/targeting/EditTargetPopulation/EditTargetPopulation';
import { useLazyInterval } from '../../../hooks/useInterval';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import {
  TargetPopulationBuildStatus,
  useTargetPopulationQuery,
} from '../../../__generated__/graphql';

export const EditTargetPopulationPage = (): React.ReactElement => {
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

  return <EditTargetPopulation targetPopulation={targetPopulation} />;
};
