import React from 'react';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import { Checkbox } from '@material-ui/core';

type Order = 'asc' | 'desc';

export interface HeadCell<T> {
  disablePadding: boolean;
  id: keyof T | string;
  label: string;
  numeric: boolean;
  weight?: number;
  dataCy?: string;
}

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

const TableSortLabelStyled = styled(TableSortLabel)`
  & {
    font-size: 12px;
  }
`;

const TableRowStyled = styled(TableRow)`
  & {
    font-size: 12px;
  }
`;

interface EnhancedTableProps<T> {
  classes: ReturnType<typeof useStyles>;
  onRequestSort: (
    event: React.MouseEvent<unknown>,
    property: keyof T | string,
  ) => void;
  order: Order;
  orderBy: string;
  rowCount: number;
  numSelected?: number;
  headCells: HeadCell<T>[];
  allowSort?: boolean;
  onSelectAllClick?: (event, rows) => void;
  data?: T[];
}

export function EnhancedTableHead<T>(
  props: EnhancedTableProps<T>,
): React.ReactElement {
  const {
    classes,
    order,
    orderBy,
    headCells,
    onRequestSort,
    allowSort = true,
    onSelectAllClick,
    rowCount,
    numSelected = 0,
    data = [],
  } = props;
  const createSortHandler = (property: keyof T | string) => (
    event: React.MouseEvent<unknown>,
  ) => {
    onRequestSort(event, property);
  };
  return (
    <TableHead>
      <TableRow>
        {onSelectAllClick && data.length ? (
          <TableCell padding='checkbox'>
            <Checkbox
              color='primary'
              indeterminate={numSelected > 0 && numSelected < rowCount}
              checked={rowCount > 0 && numSelected === rowCount}
              onChange={(event) => onSelectAllClick(event, data)}
              inputProps={{ 'aria-label': 'select all' }}
            />
          </TableCell>
        ) : null}
        {headCells.map((headCell) => (
          <TableCell
            key={headCell.id.toString()}
            align={headCell.numeric ? 'right' : 'left'}
            padding={headCell.disablePadding ? 'none' : 'default'}
            sortDirection={orderBy === headCell.id ? order : false}
            data-cy={headCell.dataCy}
          >
            {allowSort ? (
              <TableSortLabelStyled
                active={orderBy === headCell.id}
                direction={orderBy === headCell.id ? order : 'asc'}
                onClick={createSortHandler(headCell.id)}
              >
                {headCell.label}
                {orderBy === headCell.id && (
                  <span className={classes.visuallyHidden}>
                    {order === 'desc'
                      ? 'sorted descending'
                      : 'sorted ascending'}
                  </span>
                )}
              </TableSortLabelStyled>
            ) : (
              <TableRowStyled>{headCell.label}</TableRowStyled>
            )}
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
  );
}
