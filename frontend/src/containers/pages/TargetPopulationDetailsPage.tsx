import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  useTargetPopulationQuery,
  TargetPopulationNode,
} from '../../__generated__/graphql';
import { EditTargetPopulation } from '../../components/TargetPopulation/EditTargetPopulation';
import { TargetPopulationCore } from '../../components/TargetPopulation/TargetPopulationCore';
import { TargetPopulationDetails } from '../../components/TargetPopulation/TargetPopulationDetails';
import { TargetPopulationPageHeader } from './headers/TargetPopulationPageHeader';
import { usePermissions } from '../../hooks/usePermissions';
import { LoadingComponent } from '../../components/LoadingComponent';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PermissionDenied } from '../../components/PermissionDenied';

export function TargetPopulationDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const permissions = usePermissions();
  const { data, loading } = useTargetPopulationQuery({
    variables: { id },
  });
  const [isEdit, setEditState] = useState(false);

  if (loading) return <LoadingComponent />;
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.TARGETING_VIEW_DETAILS, permissions))
    return <PermissionDenied />;

  if (!data) return null;

  const targetPopulation = data.targetPopulation as TargetPopulationNode;
  const { status } = targetPopulation;

  return (
    <div>
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
          {(status === 'APPROVED' || status === 'FINALIZED') && (
            <TargetPopulationDetails targetPopulation={targetPopulation} />
          )}
          <TargetPopulationCore
            id={targetPopulation.id}
            status={status}
            candidateList={targetPopulation.candidateListTargetingCriteria}
            targetPopulation={targetPopulation}
          />
        </>
      )}
    </div>
  );
}
