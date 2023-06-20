import React from 'react';
import { useTranslation } from 'react-i18next';
import { GlobalAreaChartsQuery } from '../../../../__generated__/graphql';
import { TotalAmountTransferredByCountryChart } from '../../charts/TotalAmountTransferredByCountryChart';
import { CardTextLightLarge } from '../../DashboardCard';
import { DashboardPaper } from '../../DashboardPaper';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';

interface TotalAmountTransferredByCountrySectionProps {
  data: GlobalAreaChartsQuery['chartTotalTransferredCashByCountry'];
}
export const TotalAmountTransferredByCountrySection = ({
  data,
}: TotalAmountTransferredByCountrySectionProps): React.ReactElement => {
  const { businessArea } = useBaseUrl();
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
