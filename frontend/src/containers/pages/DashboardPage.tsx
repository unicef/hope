import React, {useState} from 'react';
import {Tab, Tabs, Typography} from '@material-ui/core';
import {PageHeader} from '../../components/PageHeader';
import {DashboardFilters} from '../../components/Dashboard/DashboardFilters';
import {ExportModal} from '../../components/Dashboard/ExportModal';
import {usePermissions} from '../../hooks/usePermissions';
import {hasPermissions, PERMISSIONS} from '../../config/permissions';
import {PermissionDenied} from '../../components/PermissionDenied';
import {useBusinessArea} from '../../hooks/useBusinessArea';
import {useDashboardYearsChoiceDataQuery} from '../../__generated__/graphql';
import {LoadingComponent} from '../../components/LoadingComponent';
import {DashboardPaper} from '../../components/Dashboard/DashboardPaper';
import {DashboardYearPage} from './DashboardYearPage';

export function DashboardPage(): React.ReactElement {
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  const [selectedTab, setSelectedTab] = useState(0);
  const [filter, setFilter] = useState({
    program: '',
    administrativeArea: undefined,
  });
  const { data, loading } = useDashboardYearsChoiceDataQuery({
    variables: { businessArea },
  });
  if (loading) return <LoadingComponent />;
  if (!permissions || !data) return null;

  const hasPermissionToView = hasPermissions(
    PERMISSIONS.DASHBOARD_VIEW_COUNTRY,
    permissions,
  );
  const hasPermissionToExport = hasPermissions(
    PERMISSIONS.DASHBOARD_EXPORT,
    permissions,
  );

  const years = data.dashboardYearsChoices;

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
          {businessArea !== 'global' ? (
            <DashboardFilters filter={filter} onFilterChange={setFilter} />
          ) : (
            <DashboardPaper noMarginTop extraPaddingLeft color='#6f6f6f'>
              <Typography variant='body2'>
                All charts below show total numbers for the selected year.
              </Typography>
            </DashboardPaper>
          )}
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
