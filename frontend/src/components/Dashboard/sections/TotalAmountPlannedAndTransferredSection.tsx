import React from 'react';
import { TotalAmountPlannedAndTransferredByCountryChart } from '../charts/TotalAmountPlannedAndTransferredByCountryChart';
import { CardTextLight } from '../DashboardCard';
import { DashboardPaper } from '../DashboardPaper';
import { AllChartsQuery } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';

interface TotalAmountPlannedAndTransferredSectionProps {
  data: AllChartsQuery['chartTotalTransferredCashByCountry'];
}
export const TotalAmountPlannedAndTransferredSection = ({
  data,
}: TotalAmountPlannedAndTransferredSectionProps): React.ReactElement => {
  const businessArea = useBusinessArea();
  if (businessArea !== 'global') {
    return null;
  }
  return (
    <DashboardPaper title='Total Amount Planned and Transferred by Country'>
      <CardTextLight>IN USD</CardTextLight>
      <TotalAmountPlannedAndTransferredByCountryChart data={data} />
    </DashboardPaper>
  );
};
