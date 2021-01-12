import React from 'react';
import {
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
  Box,
} from '@material-ui/core';

export const TotalCashTransferredByAdministrativeAreaTable = (): React.ReactElement => {
  //TODO change line below
  const data = [
    { id: '1', admin2: 'Congue', totalCashTransferred: '$11000' },
    { id: '2', admin2: 'Feugiat', totalCashTransferred: '$12000' },
    { id: '3', admin2: 'Aliquam', totalCashTransferred: '$12000' },
    { id: '4', admin2: 'Massa', totalCashTransferred: '$13000' },
    { id: '5', admin2: 'Euismod', totalCashTransferred: '$14000' },
    { id: '6', admin2: 'Moloko', totalCashTransferred: '$15000' },
    { id: '7', admin2: 'Clopreks', totalCashTransferred: '$16000' },
    { id: '8', admin2: 'Cuqierek', totalCashTransferred: '$17000' },
    { id: '9', admin2: 'Poloskwer', totalCashTransferred: '$17000' },
    { id: '10', admin2: 'Cofrotyop', totalCashTransferred: '$180000' },
  ];

  const renderRows = (): Array<React.ReactElement> => {
    return data.map((el) => {
      return (
        <TableRow key={el.id}>
          <TableCell align='left'>{el.admin2}</TableCell>
          <TableCell align='left'>{el.totalCashTransferred}</TableCell>
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
