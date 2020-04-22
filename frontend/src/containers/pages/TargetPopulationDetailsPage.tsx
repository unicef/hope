import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Tabs, Tab } from '@material-ui/core';
import { TabPanel } from '../../components/TabPanel';
import { TargetPopulationPageHeader } from './headers/TargetPopulationPageHeader';
import {
  useTargetPopulationQuery,
  TargetPopulationNode,
} from '../../__generated__/graphql';
import { EditTargetPopulation } from '../../components/TargetPopulation/EditTargetPopulation';
import { TargetPopulationCore } from '../../components/TargetPopulation/TargetPopulationCore';
import { TargetPopulationDetails } from '../../components/TargetPopulation/TargetPopulationDetails';

export function TargetPopulationDetailsPage() {
  const { id } = useParams();
  const { data, loading } = useTargetPopulationQuery({
    variables: { id },
  });
  const [isEdit, setEditState] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);

  const changeTab = (event: React.ChangeEvent<{}>, newValue: number) => {
    setSelectedTab(newValue);
  };

  if (!data) {
    return null;
  }
  const targetPopulation = data.targetPopulation as TargetPopulationNode;
  const { status } = targetPopulation;
  const tabs = (
    <Tabs
      value={selectedTab}
      onChange={changeTab}
      aria-label='tabs'
      indicatorColor='primary'
      textColor='primary'
    >
      <Tab label='Candidate list' />
      <Tab label='Target Population' disabled={status === 'DRAFT'} />
    </Tabs>
  );
  return (
    <div>
      {isEdit ? (
        <EditTargetPopulation
          targetPopulation={targetPopulation}
          selectedTab={selectedTab}
          targetPopulationCriterias={
            targetPopulation.candidateListTargetingCriteria
          }
          cancelEdit={() => setEditState(false)}
        />
      ) : (
        <>
          <TargetPopulationPageHeader
            targetPopulation={targetPopulation}
            isEditMode={isEdit}
            setEditState={setEditState}
            tabs={tabs}
            selectedTab={selectedTab}
          />
          {(status === 'APPROVED' || status === 'FINALIZED') && (
            <TargetPopulationDetails targetPopulation={targetPopulation} />
          )}
          <TabPanel value={selectedTab} index={0}>
            <TargetPopulationCore
              id={targetPopulation.id}
              candidateList={targetPopulation.candidateListTargetingCriteria}
            />
          </TabPanel>
          <TabPanel value={selectedTab} index={1}>
            <TargetPopulationCore
              id={targetPopulation.id}
              candidateList={targetPopulation.candidateListTargetingCriteria}
              targetPopulationList={targetPopulation.finalListTargetingCriteria}
              selectedTab={selectedTab}
            />
          </TabPanel>
        </>
      )}
    </div>
  );
}
