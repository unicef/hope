import React from 'react';
import {TotalAmountTransferredByCountryChart} from '../charts/TotalAmountTransferredByCountryChart';
import {CardTextLightLarge} from '../DashboardCard';
import {DashboardPaper} from '../DashboardPaper';
import {GlobalAreaChartsQuery} from '../../../__generated__/graphql';
import {useBusinessArea} from '../../../hooks/useBusinessArea';

interface TotalAmountTransferredSectionByCountryProps {
  data: GlobalAreaChartsQuery['chartTotalTransferredCashByCountry'];
}
export const TotalAmountTransferredSectionByCountry = ({
  data,
}: TotalAmountTransferredSectionByCountryProps): React.ReactElement => {
  const businessArea = useBusinessArea();

  if (businessArea !== 'global') {
    return null;
  }
  return (
    <DashboardPaper
      title='Total Transferred by Country'
      extraPaddingTitle={false}
    >
      <CardTextLightLarge>IN USD</CardTextLightLarge>
      <TotalAmountTransferredByCountryChart data={data} />
    </DashboardPaper>
  );
};
