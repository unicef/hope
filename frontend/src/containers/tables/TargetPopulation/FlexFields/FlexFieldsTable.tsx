import React, { ReactElement, useState } from 'react';
import styled from 'styled-components';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import { Table, TableHead, TableRow, TableCell, TableBody } from '@material-ui/core';
import { useFlexFieldsQuery } from '../../../../__generated__/graphql';
import { headCells } from './HeadCells';
import { FlexFieldRow } from './TableRow';
import { EnhancedTableHead } from '../../../../components/table/EnhancedTableHead';
import { stableSort, getComparator } from '../../../../utils/utils';

const TableWrapper = styled.div`
  padding: 0;
`;

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      width: '100%',
    },
    paper: {
      width: '100%',
      marginBottom: theme.spacing(2),
    },
    table: {
      minWidth: 750,
    },
    visuallyHidden: {
      border: 0,
      clip: 'rect(0 0 0 0)',
      height: 1,
      margin: -1,
      overflow: 'hidden',
      padding: 0,
      position: 'absolute',
      top: 20,
      width: 1,
    },
  }),
);

type Order = 'asc' | 'desc';

export const FlexFieldsTable = ({ fields }): ReactElement => {
  const [order, setOrder] = useState('asc');
  const [orderBy, setOrderBy] = useState('');
  const classes = useStyles({});

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  return (
    <TableWrapper>
      <Table aria-label="simple table">
        <EnhancedTableHead
          classes={classes}
          order={order as Order}
          headCells={headCells}
          orderBy={orderBy}
          onRequestSort={handleRequestSort}
          rowCount={fields.length - 1}
        />
        <TableBody>
          {stableSort(fields, getComparator(order, orderBy)).map((row) => (
            <TableRow key={row.name}>
              <TableCell component="th" scope="row">
                {row.name}
              </TableCell>
              <TableCell>{row.type}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableWrapper>
  );
};
