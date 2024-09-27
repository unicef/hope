import React, { useEffect, useState } from 'react';
import { Typography, Box, Tabs, Tab, Paper } from '@mui/material'; 
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { DashboardYearPage } from './DashboardYearPage'; 
import { useLocation } from 'react-router-dom';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TabPanel } from '@components/core/TabPanel';

export function DashboardPage(): React.ReactElement {
  const { t } = useTranslation();
  const location = useLocation();
  const permissions = usePermissions();
  const { businessArea, isGlobal } = useBaseUrl();
  const [selectedTab, setSelectedTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);
  const [selectedYear, setSelectedYear] = useState<string | null>(null); // Manage selected year
  const [availableYears, setAvailableYears] = useState<string[]>([]); // Store available years

  // Fetch data from REST API
  const fetchData = async () => {
    try {
      const response = await fetch(`/api/dashboard/${businessArea}`);
      const result = await response.json();
      setData(result);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [businessArea]);

  useEffect(() => {
    if (data.length === 0) return;

    // Extract unique years from the data
    const years = Array.from(
      new Set(
        data
          .map(household => household.payments.map(payment => new Date(payment.delivery_date).getFullYear()))
          .flat()
      )
    ).sort((a, b) => b - a); // Sort years in descending order

    setAvailableYears(years);
    setSelectedYear(years[0] || null); // Set the highest year (first in the sorted array) as default
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
          <TabPanel value={selectedTab} index={selectedTab}>
            <DashboardYearPage
              year={selectedYear}
              data={data.filter(household =>
                household.payments.some(payment => new Date(payment.delivery_date).getFullYear() === selectedYear)
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
