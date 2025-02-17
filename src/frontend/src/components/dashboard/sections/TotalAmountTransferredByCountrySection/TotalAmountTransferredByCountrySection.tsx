import { useTranslation } from 'react-i18next';
import { GlobalAreaChartsQuery } from '@generated/graphql';
import { TotalAmountTransferredByCountryChart } from '../../charts/TotalAmountTransferredByCountryChart';
import { CardTextLightLarge } from '../../DashboardCard';
import { DashboardPaper } from '../../DashboardPaper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

interface TotalAmountTransferredByCountrySectionProps {
  data: GlobalAreaChartsQuery['chartTotalTransferredCashByCountry'];
}
export function TotalAmountTransferredByCountrySection({
  data,
}: TotalAmountTransferredByCountrySectionProps): ReactElement {
  const { isGlobal } = useBaseUrl();
  const { t } = useTranslation();
  if (!isGlobal) {
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
}
