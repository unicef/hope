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
import { TargetPopulationCore } from '../dialogs/targetPopulation/TargetPopulationCore';

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

  const tabs = (
    <Tabs
      value={selectedTab}
      onChange={changeTab}
      aria-label='tabs'
      indicatorColor='primary'
      textColor='primary'
    >
      <Tab label='Candidate list' />
      <Tab label='Target Population' />
    </Tabs>
  );

  if (!data) {
    return null;
  }
  const targetPopulation = data.targetPopulation as TargetPopulationNode;

  return (
    <div>
      {isEdit ? (
        <EditTargetPopulation
          targetPopulation={targetPopulation.candidateListTargetingCriteria}
          cancelEdit={() => setEditState(false)}
        />
      ) : (
        <>
          <TargetPopulationPageHeader
            targetPopulation={targetPopulation}
            isEditMode={isEdit}
            setEditState={setEditState}
            tabs={tabs}
          />
          <TabPanel value={selectedTab} index={0}>
            <TargetPopulationCore targetPopulation={targetPopulation.candidateListTargetingCriteria} />
          </TabPanel>
          <TabPanel value={selectedTab} index={1}>
            <TargetPopulationCore targetPopulation={targetPopulation.finalListTargetingCriteria} />
          </TabPanel>
        </>
      )}
    </div>
  );
}
