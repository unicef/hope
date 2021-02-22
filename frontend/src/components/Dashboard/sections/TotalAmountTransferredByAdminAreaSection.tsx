import React from 'react';
import { CardTextLight } from '../DashboardCard';
import { DashboardPaper } from '../DashboardPaper';
import { CountryChartsQuery } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { TotalAmountTransferredByAdminAreaTable } from '../TotalAmountTransferredByAdminAreaTable';

interface TotalAmountTransferredSectionByAdminAreaSectionProps {
  data: CountryChartsQuery['tableTotalCashTransferredByAdministrativeArea'];
  handleSort;
  order;
  orderBy;
}
export const TotalAmountTransferredSectionByAdminAreaSection = ({
  data,
  handleSort,
  order,
  orderBy,
}: TotalAmountTransferredSectionByAdminAreaSectionProps): React.ReactElement => {
  const businessArea = useBusinessArea();
  if (businessArea === 'global') {
    return null;
  }
  return (
    <DashboardPaper title='Total Transferred by Administrative Area'>
      <CardTextLight>IN USD</CardTextLight>
      <TotalAmountTransferredByAdminAreaTable
        data={data?.data}
        handleSort={handleSort}
        order={order}
        orderBy={orderBy}
      />
    </DashboardPaper>
  );
};
