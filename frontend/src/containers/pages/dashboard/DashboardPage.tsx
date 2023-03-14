import { Tab, Tabs, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { DashboardFilters } from '../../../components/dashboard/DashboardFilters';
import { DashboardPaper } from '../../../components/dashboard/DashboardPaper';
import { ExportModal } from '../../../components/dashboard/ExportModal';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useDashboardYearsChoiceDataQuery } from '../../../__generated__/graphql';
import { DashboardYearPage } from './DashboardYearPage';
import { getFilterFromQueryParams } from '../../../utils/utils';

export const DashboardPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  const [selectedTab, setSelectedTab] = useState(0);
  const initialFilter = {
    program: '',
    administrativeArea: '',
  };
  const [filter, setFilter] = useState(
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
      <PageHeader tabs={tabs} title={t('Dashboard')}>
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
                {t(
                  'All charts below show total numbers for the selected year.',
                )}
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
};
