import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissionInModule } from '../../../config/permissions';
import { Tabs, Tab } from '@core/Tabs';

export const HouseholdMembersPage = (): React.ReactElement => {
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();
  const navigate = useNavigate();

  const isIndividuals = location.pathname.indexOf('individuals') !== -1;

  const [selectedTab, setSelectedTab] = useState(isIndividuals ? 0 : 1);

  const householdMembersTypes = ['INDIVIDUALS', 'PERIODIC DATA UPDATES'];

  //TODO MS - Add the correct paths for the tabs
  const individualsPath = `/${baseUrl}/household-members/individuals`;
  const periodicDataUpdatesPath = `/${baseUrl}/household-members/periodic-data-updates`;

  const mappedTabs = householdMembersTypes.map((el) => (
    <Tab data-cy={`tab-${el}`} key={el} label={el} />
  ));
  const tabs = (
    <Tabs
      value={selectedTab}
      onChange={(_event, newValue: number) => {
        setSelectedTab(newValue);
        navigate(newValue === 0 ? individualsPath : periodicDataUpdatesPath);
      }}
      indicatorColor="primary"
      textColor="primary"
      variant="scrollable"
      scrollButtons="auto"
      aria-label="tabs"
    >
      {mappedTabs}
    </Tabs>
  );

  if (permissions === null) return null;
  if (!hasPermissionInModule('HOUSEHOLD_MEMBERS_VIEW_LIST', permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader tabs={tabs} title="Household Members" />
      {selectedTab === 0 ? (
        <div>Individuals Component</div>
      ) : (
        <div>Periodic Data Updates Component</div>
      )}
    </>
  );
};
