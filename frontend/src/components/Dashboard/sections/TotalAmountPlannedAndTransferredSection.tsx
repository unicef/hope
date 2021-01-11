import React from 'react';
import { CardTextLight } from '../DashboardCard';
import { DashboardPaper } from '../DashboardPaper';

export const TotalAmountPlannedAndTransferredSection = (): React.ReactElement => {
  return (
    <DashboardPaper title='Total Amount Planned and Transferred by Country'>
      <CardTextLight>IN USD</CardTextLight>
      <div>Chart here</div>
    </DashboardPaper>
  );
};
