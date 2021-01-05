import React, { useState } from 'react';
import { Tabs, Tab, Button } from '@material-ui/core';
import { PageHeader } from '../../components/PageHeader';
import { TabPanel } from '../../components/TabPanel';

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
    </TabPanel>
  );
}
