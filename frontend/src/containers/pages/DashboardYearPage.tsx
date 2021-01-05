import React from 'react';
import { TabPanel } from '../../components/TabPanel';
import { DashboardCard } from '../../components/Dashboard/DashboardCard';

interface DashboardYearPageProps {
  year: string;
  selectedTab: number;
}
export function DashboardYearPage({
  year,
  selectedTab,
}: DashboardYearPageProps): React.ReactElement {
  return (
    <TabPanel value={selectedTab} index={selectedTab}>
      Year content {year}
      <DashboardCard color='red' />
    </TabPanel>
  );
}
