import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useCountryChartsLazyQuery } from '../../../__generated__/graphql';
import { LoadingComponent } from '../../LoadingComponent';
import { CardTextLightLarge } from '../DashboardCard';
import { DashboardPaper } from '../DashboardPaper';
import { TotalAmountTransferredByAdminAreaTable } from '../TotalAmountTransferredByAdminAreaTable';

interface TotalAmountTransferredSectionByAdminAreaSectionProps {
  year: string;
  filter;
}
export const TotalAmountTransferredSectionByAdminAreaSection = ({
  year,
  filter,
}: TotalAmountTransferredSectionByAdminAreaSectionProps): React.ReactElement => {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();
  const [orderBy, setOrderBy] = useState('totalCashTransferred');
  const [order, setOrder] = useState('desc');

  const variables = {
    year: parseInt(year, 10),
    businessAreaSlug: businessArea,
    program: filter.program,
    administrativeArea: filter.administrativeArea?.node?.id,
  };
  const [
    loadCountry,
    {
      data: countryData,
      loading: countryLoading,
      refetch: refetchAdminAreaChart,
    },
  ] = useCountryChartsLazyQuery({
    variables: {
      ...variables,
      orderBy,
      order,
    },
  });

  useEffect(() => {
    if (businessArea !== 'global') {
      loadCountry();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [businessArea]);

  const handleSortAdminArea = (event, property): void => {
    let direction = '';
    if (property !== orderBy) {
      setOrderBy(property.toString());
      direction = order;
    } else {
      direction = order === 'desc' ? 'asc' : 'desc';
      setOrder(direction);
    }
    const variablesRefetch = {
      ...variables,
      orderBy: property,
      order: direction,
    };
    refetchAdminAreaChart(variablesRefetch);
  };

  if (countryLoading) return <LoadingComponent />;

  if (businessArea === 'global' || !countryData) {
    return null;
  }

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
};
