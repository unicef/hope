import { Typography } from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useDashboardYearsChoiceDataQuery } from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { DashboardFilters } from '@components/dashboard/DashboardFilters';
import { DashboardPaper } from '@components/dashboard/DashboardPaper';
import { ExportModal } from '@components/dashboard/ExportModal';
import { Tabs, Tab } from '@core/Tabs';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { DashboardYearPage } from './DashboardYearPage';
import { TabPanel } from '@components/core/TabPanel';

export function DashboardPage(): React.ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const permissions = usePermissions();
  const { businessArea, isGlobal } = useBaseUrl();
  const [selectedTab, setSelectedTab] = useState(0);
  const initialFilter = {
    administrativeArea: '',
    program: '',
  };
  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

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
      onChange={(_event: React.ChangeEvent<object>, newValue: number) => {
        setSelectedTab(newValue);
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
  return (
    <>
      <PageHeader tabs={tabs} title={t('Dashboard')}>
        {hasPermissionToExport && (
          <ExportModal filter={appliedFilter} year={years[selectedTab]} />
        )}
      </PageHeader>
      {hasPermissionToView ? (
        <>
          {!isGlobal ? (
            <DashboardFilters
              filter={filter}
              setFilter={setFilter}
              initialFilter={initialFilter}
              appliedFilter={appliedFilter}
              setAppliedFilter={setAppliedFilter}
            />
          ) : (
            <DashboardPaper noMarginTop extraPaddingLeft color="#6f6f6f">
              <Typography variant="body2">
                {t(
                  'All charts below show total numbers for the selected year.',
                )}
              </Typography>
            </DashboardPaper>
          )}
          <TabPanel value={selectedTab} index={selectedTab}>
            <DashboardYearPage
              year={years[selectedTab]}
              filter={appliedFilter}
            />
          </TabPanel>
        </>
      ) : (
        <PermissionDenied />
      )}
    </>
  );
}
