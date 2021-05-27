import React from 'react';
import {Table, TableBody, TableCell, TableRow} from '@material-ui/core';
import {CountryChartsQuery} from '../../__generated__/graphql';
import {formatCurrency, formatNumber} from '../../utils/utils';
import {EnhancedTableHead} from '../table/EnhancedTableHead';

interface TotalAmountTransferredByAdminAreaTableProps {
  data: CountryChartsQuery['tableTotalCashTransferredByAdministrativeArea']['data'];
  handleSort;
  order;
  orderBy;
}
type Order = 'asc' | 'desc';

const headCells = [
  {
    disablePadding: false,
    label: 'Administrative Area 2',
    id: 'admin2',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Total Transferred',
    id: 'totalCashTransferred',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Households Reached',
    id: 'totalHouseholds',
    numeric: true,
  },
];
export const TotalAmountTransferredByAdminAreaTable = ({
  data,
  handleSort,
  order,
  orderBy,
}: TotalAmountTransferredByAdminAreaTableProps): React.ReactElement => {
  if (!data) return null;

  const renderRows = (): Array<React.ReactElement> => {
    return data.map((el) => {
      return (
        <TableRow key={el.id}>
          <TableCell align='left'>{el.admin2}</TableCell>
          <TableCell align='right'>
            {formatCurrency(el.totalCashTransferred, true)}
          </TableCell>
          <TableCell align='right'>
            {formatNumber(el.totalHouseholds)}
          </TableCell>
        </TableRow>
      );
    });
  };

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
};
