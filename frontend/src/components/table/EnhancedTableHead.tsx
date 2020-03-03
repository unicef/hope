import React from 'react';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';

type Order = 'asc' | 'desc';

export interface HeadCell<T> {
  disablePadding: boolean;
  id: keyof T | string;
  label: string;
  numeric: boolean;
  weight?: number;
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

interface EnhancedTableProps<T> {
  classes: ReturnType<typeof useStyles>;
  onRequestSort: (event: React.MouseEvent<unknown>, property: keyof T | string) => void;
  order: Order;
  orderBy: keyof T;
  rowCount: number;
  headCells: HeadCell<T>[];
}

export function EnhancedTableHead<T>(
  props: EnhancedTableProps<T>,
): React.ReactElement {
  const { classes, order, orderBy, headCells, onRequestSort } = props;
  const createSortHandler = (property: keyof T | string) => (
    event: React.MouseEvent<unknown>,
  ) => {
    onRequestSort(event, property);
  };

  return (
    <TableHead>
      <TableRow>
        {headCells.map((headCell) => (
          <TableCell
            key={headCell.id.toString()}
            align={headCell.numeric ? 'right' : 'left'}
            padding={headCell.disablePadding ? 'none' : 'default'}
            sortDirection={orderBy === headCell.id ? order : false}
          >
            <TableSortLabelStyled
              active={orderBy === headCell.id}
              direction={orderBy === headCell.id ? order : 'asc'}
              onClick={createSortHandler(headCell.id)}
            >
              {headCell.label}
              {orderBy === headCell.id ? (
                <span className={classes.visuallyHidden}>
                  {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                </span>
              ) : null}
            </TableSortLabelStyled>
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
  );
}
