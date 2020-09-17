import React, { ReactElement, useState } from 'react';
import styled from 'styled-components';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import { Table, TableRow, TableCell, TableBody } from '@material-ui/core';
import { EnhancedTableHead } from '../../../../components/table/EnhancedTableHead';
import { stableSort, getComparator } from '../../../../utils/utils';
import { headCells } from './HeadCells';

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

const StyledHeaderCell = styled(TableCell)`
  && {
    border-bottom: 0;
  }
`;

type Order = 'asc' | 'desc';

export const FlexFieldsTable = ({
  fields,
  selectedOption,
  searchValue,
}): ReactElement => {
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
      associatedWith: selectedOption,
    };
    return fields.map((field) => {
      if (!searchValue && !selectedOption) {
        return field;
      }
      return {
        ...field,
        flexAttributes: field.flexAttributes.filter((each) => {
          //eslint-disable-next-line
          for (const key in filters) {
            if (
              each[key] === undefined ||
              (each[key] !== filters[key] &&
                !each[key].toLowerCase().includes(filters[key].toLowerCase()))
            ) {
              return false;
            }
          }
          return true;
        }),
      };
    });
  };

  const orderResults = () => {
    return filterTable().map((each) => {
      return {
        ...each,
        flexAttributes: stableSort(
          each.flexAttributes,
          getComparator(order, orderBy),
        ),
      };
    });
  };

  return (
    <TableWrapper>
      <Table aria-label='simple table'>
        <EnhancedTableHead
          classes={classes}
          order={order as Order}
          headCells={headCells}
          orderBy={orderBy}
          onRequestSort={handleRequestSort}
          rowCount={fields.length - 1}
        />
        <TableBody>
          {orderResults().map((row) => (
            <>
              <TableRow key={row.id}>
                <StyledHeaderCell>
                  <b>{row.labelEn}</b>
                </StyledHeaderCell>
              </TableRow>
              {row.flexAttributes?.map((attribute) => (
                <TableRow key={attribute.id}>
                  <StyledCell>{attribute.labelEn}</StyledCell>
                  <TableCell>{attribute.associatedWith}</TableCell>
                </TableRow>
              ))}
            </>
          ))}
        </TableBody>
      </Table>
    </TableWrapper>
  );
};
