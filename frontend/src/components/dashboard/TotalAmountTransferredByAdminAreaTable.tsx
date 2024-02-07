import { Table, TableBody, TableCell, TableRow } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { formatCurrency, formatNumber } from '@utils/utils';
import { CountryChartsQuery } from '../../__generated__/graphql';
import { EnhancedTableHead } from '../core/Table/EnhancedTableHead';

interface TotalAmountTransferredByAdminAreaTableProps {
  data: CountryChartsQuery['tableTotalCashTransferredByAdministrativeArea']['data'];
  handleSort;
  order;
  orderBy;
}
type Order = 'asc' | 'desc';

export function TotalAmountTransferredByAdminAreaTable({
  data,
  handleSort,
  order,
  orderBy,
}: TotalAmountTransferredByAdminAreaTableProps): React.ReactElement {
  const { t } = useTranslation();

  const headCells = [
    {
      disablePadding: false,
      label: t('Administrative Area 2'),
      id: 'admin2',
      numeric: false,
    },
    {
      disablePadding: false,
      label: t('Total Transferred'),
      id: 'totalCashTransferred',
      numeric: true,
    },
    {
      disablePadding: false,
      label: t('Households Reached'),
      id: 'totalHouseholds',
      numeric: true,
    },
  ];
  if (!data) return null;

  const renderRows = (): Array<React.ReactElement> =>
    data.map((el) => (
      <TableRow key={el.id}>
        <TableCell align="left">{el.admin2}</TableCell>
        <TableCell align="right">
          {formatCurrency(el.totalCashTransferred, true)}
        </TableCell>
        <TableCell align="right">{formatNumber(el.totalHouseholds)}</TableCell>
      </TableRow>
    ));

  return (
    <Table>
      <EnhancedTableHead
        order={order as Order}
        orderBy={orderBy}
        headCells={headCells}
        rowCount={data.length}
        onRequestSort={handleSort}
      />
      <TableBody>{renderRows()}</TableBody>
    </Table>
  );
}
