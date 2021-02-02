import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@material-ui/core';
import { AllChartsQuery } from '../../__generated__/graphql';

interface TotalCashTransferredByAdministrativeAreaTableProps {
  data: AllChartsQuery['tableTotalCashTransferredByAdministrativeArea']['data'];
}
export const TotalCashTransferredByAdministrativeAreaTable = ({
  data,
}: TotalCashTransferredByAdministrativeAreaTableProps): React.ReactElement => {
  const renderRows = (): Array<React.ReactElement> => {
    return data.map((el) => {
      return (
        <TableRow key={el.id}>
          <TableCell align='left'>{el.admin2}</TableCell>
          <TableCell align='left'>
            {parseFloat(el.totalCashTransferred).toFixed(2)}
          </TableCell>
        </TableRow>
      );
    });
  };

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell align='left'>Administrative Level 2</TableCell>
          <TableCell align='left'>Total Cash Transferred</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>{renderRows()}</TableBody>
    </Table>
  );
};
