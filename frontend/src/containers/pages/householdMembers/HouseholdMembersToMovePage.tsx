import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '@components/core/PageHeader';
import { Tabs, Tab } from '@core/Tabs';
import { PeriodicDataUpdates } from '@components/periodicDataUpdates/PeriodicDataUpdates';
import { useBaseUrl } from '@hooks/useBaseUrl';

export const HouseholdMembersToMovePage = () => {
  const { baseUrl } = useBaseUrl();
  const navigate = useNavigate();

  const [selectedTab, setSelectedTab] = useState(0);

  const individualsPath = `/${baseUrl}/population/household-members/individuals`;
  const periodicDataUpdatesPath = `/${baseUrl}/population/household-members/periodic-data-updates`;

  const handleTabChange = (newValue) => {
    setSelectedTab(newValue);
    navigate(newValue === 0 ? individualsPath : periodicDataUpdatesPath);
  };

  const renderTabContent = () => {
    switch (selectedTab) {
      case 0:
        return <div>Individuals Content</div>;
      case 1:
        return <PeriodicDataUpdates />;
      default:
        return null;
    }
  };

  return (
    <>
      <PageHeader
        tabs={
          <Tabs
            value={selectedTab}
            onChange={(_, newValue) => handleTabChange(newValue)}
            indicatorColor="primary"
            textColor="primary"
            variant="scrollable"
            scrollButtons="auto"
            aria-label="tabs"
          >
            <Tab label="Individuals" data-cy="tab-Individuals" />
            <Tab
              label="Periodic Data Updates"
              data-cy="tab-PeriodicDataUpdates"
            />
          </Tabs>
        }
        title="Household Members"
      />
      {renderTabContent()}
    </>
  );
};
