import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { EnrollmentCore } from '../../../components/enrollment/EnrollmentDetails/EnrollmentCore';
import { EnrollmentDetails } from '../../../components/enrollment/EnrollmentDetails/EnrollmentDetails';
import { EnrollmentPageHeader } from '../../../components/enrollment/EnrollmentDetails/EnrollmentPageHeader';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import {
  TargetPopulationBuildStatus,
  useTargetPopulationQuery,
} from '../../../__generated__/graphql';

export const EnrollmentDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const {
    data,
    loading,
    error,
    startPolling,
    stopPolling,
  } = useTargetPopulationQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });

  const buildStatus = data?.targetPopulation?.buildStatus;
  useEffect(() => {
    if (
      [
        TargetPopulationBuildStatus.Building,
        TargetPopulationBuildStatus.Pending,
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

  if (!data || permissions === null) return null;

  const { targetPopulation } = data;

  const canDuplicate =
    hasPermissions(PERMISSIONS.ENROLLMENT_DUPLICATE, permissions) &&
    Boolean(targetPopulation.targetingCriteria);

  return (
    <>
      <EnrollmentPageHeader
        targetPopulation={targetPopulation}
        canEdit={hasPermissions(PERMISSIONS.ENROLLMENT_UPDATE, permissions)}
        canRemove={hasPermissions(PERMISSIONS.ENROLLMENT_REMOVE, permissions)}
        canDuplicate={canDuplicate}
        canLock={hasPermissions(PERMISSIONS.ENROLLMENT_LOCK, permissions)}
        canUnlock={hasPermissions(PERMISSIONS.ENROLLMENT_UNLOCK, permissions)}
      />
      <EnrollmentDetails targetPopulation={targetPopulation} />
      <EnrollmentCore
        id={targetPopulation.id}
        targetPopulation={targetPopulation}
        permissions={permissions}
      />
    </>
  );
};
