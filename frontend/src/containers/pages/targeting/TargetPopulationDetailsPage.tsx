import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  useTargetPopulationQuery,
  TargetPopulationNode,
} from '../../../__generated__/graphql';
import { EditTargetPopulation } from '../../../components/targeting/EditTargetPopulation/EditTargetPopulation';
import { TargetPopulationCore } from '../../../components/targeting/TargetPopulationCore';
import { TargetPopulationDetails } from '../../../components/targeting/TargetPopulationDetails';
import { usePermissions } from '../../../hooks/usePermissions';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { isPermissionDeniedError } from '../../../utils/utils';
import { TargetPopulationPageHeader } from '../headers/TargetPopulationPageHeader';

export function TargetPopulationDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading, error } = useTargetPopulationQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const [isEdit, setEditState] = useState(false);

  if (loading) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null) return null;

  const targetPopulation = data.targetPopulation as TargetPopulationNode;
  const { status } = targetPopulation;

  return (
    <>
      {isEdit ? (
        <EditTargetPopulation
          targetPopulation={targetPopulation}
          targetPopulationCriterias={
            targetPopulation.candidateListTargetingCriteria
          }
          cancelEdit={() => setEditState(false)}
        />
      ) : (
        <>
          <TargetPopulationPageHeader
            targetPopulation={targetPopulation}
            setEditState={setEditState}
            canEdit={hasPermissions(PERMISSIONS.TARGETING_UPDATE, permissions)}
            canRemove={hasPermissions(
              PERMISSIONS.TARGETING_REMOVE,
              permissions,
            )}
            canDuplicate={hasPermissions(
              PERMISSIONS.TARGETING_DUPLICATE,
              permissions,
            )}
            canLock={hasPermissions(PERMISSIONS.TARGETING_LOCK, permissions)}
            canUnlock={hasPermissions(
              PERMISSIONS.TARGETING_UNLOCK,
              permissions,
            )}
            canSend={hasPermissions(PERMISSIONS.TARGETING_SEND, permissions)}
          />
          {status !== 'DRAFT' && (
            <TargetPopulationDetails targetPopulation={targetPopulation} />
          )}
          <TargetPopulationCore
            id={targetPopulation.id}
            status={status}
            candidateList={targetPopulation.candidateListTargetingCriteria}
            targetPopulation={targetPopulation}
            permissions={permissions}
          />
        </>
      )}
    </>
  );
}
