import React from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { GlobalAreaChartsQuery } from '../../../__generated__/graphql';
import { TotalAmountTransferredByCountryChart } from '../charts/TotalAmountTransferredByCountryChart';
import { CardTextLightLarge } from '../DashboardCard';
import { DashboardPaper } from '../DashboardPaper';

interface TotalAmountTransferredSectionByCountryProps {
  data: GlobalAreaChartsQuery['chartTotalTransferredCashByCountry'];
}
export const TotalAmountTransferredSectionByCountry = ({
  data,
}: TotalAmountTransferredSectionByCountryProps): React.ReactElement => {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();
  if (businessArea !== 'global') {
    return null;
  }
  return (
    <DashboardPaper
      title={t('Total Transferred by Country')}
      extraPaddingTitle={false}
    >
      <CardTextLightLarge>{t('IN USD')}</CardTextLightLarge>
      <TotalAmountTransferredByCountryChart data={data} />
    </DashboardPaper>
  );
};
