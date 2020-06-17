import React, { ReactElement, useState } from 'react';
import styled from 'styled-components';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import { Table, TableRow, TableCell, TableBody } from '@material-ui/core';
import { headCells } from './HeadCells';
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

const StyledCell = styled(TableCell)`
  width: 70%;
`;

type Order = 'asc' | 'desc';

export const FlexFieldsTable = ({ fields, selectedOption, searchValue }): ReactElement => {
  const [order, setOrder] = useState('asc');
  const [orderBy, setOrderBy] = useState('');
  const classes = useStyles({});

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const filterTable = () => {
    const filters = {
      labelEn: searchValue,
      associatedWith: selectedOption
    };
    return fields.filter(field => {
      if(!searchValue && !selectedOption) {
        return true;
      }
      //eslint-disable-next-line
      for (const key in filters) {
        if (field[key] === undefined || (field[key] !== filters[key] && !field[key].includes(filters[key]))) {
          return false;
        }
      }
      return true;
    })
  };

  const filteredFields = filterTable()
  
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
          {stableSort(filteredFields, getComparator(order, orderBy)).map((row) => (
            <TableRow key={row.id}>
              <StyledCell>
                {row.labelEn}
              </StyledCell>
              <TableCell>{row.associatedWith}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableWrapper>
  );
};
