import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useCountryChartsLazyQuery } from '@generated/graphql';
import { LoadingComponent } from '@core/LoadingComponent';
import { CardTextLightLarge } from '../../DashboardCard';
import { DashboardPaper } from '../../DashboardPaper';
import { TotalAmountTransferredByAdminAreaTableForPeople } from './TotalAmountTransferredByAdminAreaTableForPeople';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface TotalAmountTransferredSectionByAdminAreaSectionForPeopleProps {
  year: string;
  filter;
}
export function TotalAmountTransferredSectionByAdminAreaForPeopleSection({
  year,
  filter,
}: TotalAmountTransferredSectionByAdminAreaSectionForPeopleProps): React.ReactElement {
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
  const [loadData, { data, loading }] = useCountryChartsLazyQuery({
    variables: {
      ...variables,
      orderBy,
      order,
    },
    fetchPolicy: 'cache-and-network',
  });

  useEffect(() => {
    void loadData();
  }, [loadData, orderBy, order]);

  const handleSortAdminArea = (_: any, property: string): void => {
    if (property !== orderBy) {
      setOrderBy(property.toString());
      setOrder('desc');
    } else {
      setOrder((currOrder) => (currOrder === 'desc' ? 'asc' : 'desc'));
    }
  };

  if (loading) return <LoadingComponent />;
  if (!data) return null;

  return (
    <DashboardPaper
      title={t('Total Transferred by Administrative Area')}
      extraPaddingTitle={false}
    >
      <CardTextLightLarge>{t('IN USD')}</CardTextLightLarge>
      <TotalAmountTransferredByAdminAreaTableForPeople
        data={
          data?.tableTotalCashTransferredByAdministrativeAreaForPeople?.data
        }
        handleSort={handleSortAdminArea}
        order={order}
        orderBy={orderBy}
      />
    </DashboardPaper>
  );
}
