import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Tabs, Tab } from '@material-ui/core';
import { TabPanel } from '../../components/TabPanel';
import {
  useTargetPopulationQuery,
  TargetPopulationNode,
} from '../../__generated__/graphql';
import { EditTargetPopulation } from '../../components/TargetPopulation/EditTargetPopulation';
import { TargetPopulationCore } from '../../components/TargetPopulation/TargetPopulationCore';
import { TargetPopulationDetails } from '../../components/TargetPopulation/TargetPopulationDetails';
import { TargetPopulationPageHeader } from './headers/TargetPopulationPageHeader';
import { TargetPopulationProgramme } from '../../components/TargetPopulation/TargetPopulationProgramme';

export function TargetPopulationDetailsPage(): React.ReactElement {

  const { id } = useParams();
  const { data } = useTargetPopulationQuery({
    variables: { id },
  });
  const [isEdit, setEditState] = useState(false);
  if (!data) {
    return null;
  }
  const targetPopulation = data.targetPopulation as TargetPopulationNode;
  const { status } = targetPopulation;

  return (
    <div>
      {isEdit ? (
        <>
        <EditTargetPopulation
          targetPopulation={targetPopulation}
          targetPopulationCriterias={
            targetPopulation.candidateListTargetingCriteria
          }
          cancelEdit={() => setEditState(false)}
        />
        </>
      ) : (
        <>
          <TargetPopulationPageHeader
            targetPopulation={targetPopulation}
            setEditState={setEditState}
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
