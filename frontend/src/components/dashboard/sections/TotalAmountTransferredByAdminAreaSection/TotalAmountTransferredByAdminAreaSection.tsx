import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useCountryChartsLazyQuery } from '@generated/graphql';
import { LoadingComponent } from '@core/LoadingComponent';
import { CardTextLightLarge } from '../../DashboardCard';
import { DashboardPaper } from '../../DashboardPaper';
import { TotalAmountTransferredByAdminAreaTable } from './TotalAmountTransferredByAdminAreaTable';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface TotalAmountTransferredSectionByAdminAreaSectionProps {
  year: string;
  filter;
}
export function TotalAmountTransferredSectionByAdminAreaSection({
  year,
  filter,
}: TotalAmountTransferredSectionByAdminAreaSectionProps): React.ReactElement {
  const { t } = useTranslation();
  const [orderBy, setOrderBy] = useState('totalCashTransferred');
  const [order, setOrder] = useState('desc');
  const { businessArea, programId } = useBaseUrl();
  const variables = {
    year: parseInt(year, 10),
    businessAreaSlug: businessArea,
    program: programId,
    administrativeArea: filter.administrativeArea?.node?.id,
  };
  const [loadCountry, { data: countryData, loading: countryLoading }] =
    useCountryChartsLazyQuery({
      variables: {
        ...variables,
        orderBy,
        order,
      },
      fetchPolicy: 'cache-and-network',
    });

  useEffect(() => {
    void loadCountry();
  }, [loadCountry, orderBy, order]);

  const handleSortAdminArea = (_, property): void => {
    if (property !== orderBy) {
      setOrderBy(property.toString());
      setOrder('desc');
    } else {
      setOrder((currOrder) => (currOrder === 'desc' ? 'asc' : 'desc'));
    }
  };

  if (countryLoading) return <LoadingComponent />;
  if (!countryData) return null;

  return (
    <DashboardPaper
      title={t('Total Transferred by Administrative Area')}
      extraPaddingTitle={false}
    >
      <CardTextLightLarge>{t('IN USD')}</CardTextLightLarge>
      <TotalAmountTransferredByAdminAreaTable
        data={countryData?.tableTotalCashTransferredByAdministrativeArea?.data}
        handleSort={handleSortAdminArea}
        order={order}
        orderBy={orderBy}
      />
    </DashboardPaper>
  );
}
