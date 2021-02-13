import React, { useState } from 'react';
import { Tabs, Tab } from '@material-ui/core';
import { PageHeader } from '../../components/PageHeader';
import { DashboardFilters } from '../../components/Dashboard/DashboardFilters';
import { ExportModal } from '../../components/Dashboard/ExportModal';
import { usePermissions } from '../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PermissionDenied } from '../../components/PermissionDenied';
import { DashboardYearPage } from './DashboardYearPage';

export function DashboardPage(): React.ReactElement {
  const permissions = usePermissions();
  const [selectedTab, setSelectedTab] = useState(0);
  const [filter, setFilter] = useState({
    program: '',
    administrativeArea: '',
  });
  if (!permissions) return null;

  const hasPermissionToView = hasPermissions(
    PERMISSIONS.DASHBOARD_VIEW_COUNTRY,
    permissions,
  );
  const hasPermissionToExport = hasPermissions(
    PERMISSIONS.DASHBOARD_EXPORT,
    permissions,
  );

  const years = [
    '2021',
    '2020',
    '2019',
    '2018',
    '2017',
    '2016',
    '2015',
    '2014',
    '2013',
    '2012',
    '2011',
    '2010',
  ];

  const mappedTabs = years.map((el) => <Tab key={el} label={el} />);
  const tabs = (
    <Tabs
      value={selectedTab}
      onChange={(event: React.ChangeEvent<{}>, newValue: number) => {
        setSelectedTab(newValue);
      }}
      indicatorColor='primary'
      textColor='primary'
      variant='scrollable'
      scrollButtons='auto'
      aria-label='tabs'
    >
      {mappedTabs}
    </Tabs>
  );
  return (
    <>
      <PageHeader tabs={tabs} title='Dashboard'>
        {hasPermissionToExport && (
          <ExportModal filter={filter} year={years[selectedTab]} />
        )}
      </PageHeader>
      {hasPermissionToView ? (
        <>
          <DashboardFilters filter={filter} onFilterChange={setFilter} />
          <DashboardYearPage
            selectedTab={selectedTab}
            year={years[selectedTab]}
            filter={filter}
          />
        </>
      ) : (
        <PermissionDenied />
      )}
    </>
  );
}
