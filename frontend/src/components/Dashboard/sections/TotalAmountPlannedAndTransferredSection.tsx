import React from 'react';
import { TotalAmountPlannedAndTransferredByCountryChart } from '../charts/TotalAmountPlannedAndTransferredByCountryChart';
import { CardTextLight } from '../DashboardCard';
import { DashboardPaper } from '../DashboardPaper';

export const TotalAmountPlannedAndTransferredSection = (): React.ReactElement => {
  return (
    <DashboardPaper title='Total Amount Planned and Transferred by Country'>
      <CardTextLight>IN USD</CardTextLight>
      <TotalAmountPlannedAndTransferredByCountryChart />
    </DashboardPaper>
  );
};
