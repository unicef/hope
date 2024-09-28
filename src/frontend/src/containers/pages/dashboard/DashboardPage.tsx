import React, { useEffect, useState } from 'react';
import { Typography, Box, Tabs, Tab } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { DashboardYearPage } from './DashboardYearPage';
import { DashboardPaper } from '@components/dashboard/DashboardPaper';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TabPanel } from '@components/core/TabPanel';
import { fetchDashboardData, Household } from '@api/dashboardApi';

export function DashboardPage(): React.ReactElement {
  const { t } = useTranslation();
  const permissions = usePermissions();
  const { businessArea, isGlobal } = useBaseUrl();
  const [selectedTab, setSelectedTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<Household[]>([]);
  const [selectedYear, setSelectedYear] = useState<string | null>(null);
  const [availableYears, setAvailableYears] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await fetchDashboardData(businessArea);
        setData(result);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, [businessArea]);

  useEffect(() => {
    if (data.length === 0) return;

    const years = Array.from(
      new Set(
        data.map((household) =>
          household.payments.map((payment) => new Date(payment.delivery_date).getFullYear()),
        ).flat(),
      ),
    ).sort((a, b) => b - a); // Sort years in descending order

    setAvailableYears(years.map(String));
    setSelectedYear(years[0]?.toString() || null); // Set the highest year as default
  }, [data]);

  if (loading) return <LoadingComponent />;
  if (!permissions || !data) return null;

  const hasPermissionToView = hasPermissions(
    PERMISSIONS.DASHBOARD_VIEW_COUNTRY,
    permissions,
  );

  const mappedTabs = availableYears.map((year) => <Tab key={year} label={year} />);
  const tabs = (
    <Tabs
      value={selectedTab}
      onChange={(_event: React.ChangeEvent<object>, newValue: number) => {
        setSelectedTab(newValue);
        setSelectedYear(availableYears[newValue]);
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
      <PageHeader tabs={tabs} title={t('Dashboard')} />
      {hasPermissionToView ? (
        <>
          {!isGlobal ? (
            <Box p={0}>
            </Box>
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
              year={selectedYear}
              data={data.filter((household) =>
                household.payments.some(
                  (payment) =>
                    new Date(payment.delivery_date).getFullYear() === Number(selectedYear),
                ),
              )}
            />
          </TabPanel>
        </>
      ) : (
        <PermissionDenied />
      )}
    </>
  );
}
