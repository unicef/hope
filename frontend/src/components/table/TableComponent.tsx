import React from 'react';
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TablePagination from '@material-ui/core/TablePagination';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import { LoadingComponent } from '../LoadingComponent';
import { EnhancedTableToolbar } from './EnhancedTableToolbar';
import { EnhancedTableHead, HeadCell } from './EnhancedTableHead';
import FindInPageIcon from '@material-ui/icons/FindInPage';
import { Box } from '@material-ui/core';

export type Order = 'asc' | 'desc';

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
    empty: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
      color: 'rgba(0, 0, 0, 0.38)',
      fontSize: '24px',
      lineHeight: '28px',
      textAlign: 'center',
      padding: '70px',
    },
    smallerText: {
      fontSize: '16px',
    },
    icon: {
      fontSize: '50px',
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

interface TableComponentProps<T> {
  data: T[];
  renderRow: (row: T) => React.ReactElement;
  headCells: HeadCell<T>[];
  rowsPerPageOptions: number[];
  rowsPerPage: number;
  page: number;
  itemsCount: number;
  handleChangePage: (event: unknown, newPage: number) => void;
  handleChangeRowsPerPage: (event: React.ChangeEvent<HTMLInputElement>) => void;
  handleRequestSort: (
    event: React.MouseEvent<unknown>,
    property: string,
  ) => void;
  orderBy: string;
  order: Order;
  title?: string;
  loading?: boolean;
  allowSort?: boolean;
  isOnPaper?: boolean;
  actions?: Array<React.ReactElement>;
}

export function TableComponent<T>({
  title,
  renderRow,
  data,
  headCells,
  rowsPerPageOptions,
  rowsPerPage,
  page,
  itemsCount,
  handleChangePage,
  handleChangeRowsPerPage,
  handleRequestSort,
  order,
  orderBy,
  loading,
  allowSort,
  isOnPaper = true,
  actions,
}: TableComponentProps<T>): React.ReactElement {
  const classes = useStyles({});

  const emptyRows = itemsCount
    ? rowsPerPage - Math.min(rowsPerPage, itemsCount - page * rowsPerPage)
    : rowsPerPage;
  let body;
  if (loading) {
    body = (
      <TableRow style={{ height: 53 * emptyRows, minHeight: 53 }}>
        <TableCell colSpan={headCells.length}>
          <LoadingComponent />
        </TableCell>
      </TableRow>
    );
  } else if (!data.length) {
    body = (
      <TableRow style={{ height: 53 * emptyRows, minHeight: 53 }}>
        <TableCell colSpan={headCells.length}>
          <div className={classes.empty}>
            <FindInPageIcon className={classes.icon} fontSize='inherit' />
            <Box mt={2}>No results</Box>
            <Box className={classes.smallerText} mt={2}>
              Try adjusting your search or your filters to find what you&apos;re
              looking for.
            </Box>
          </div>
        </TableCell>
      </TableRow>
    );
  } else {
    body = (
      <>
        {data.map((row) => {
          return renderRow(row);
        })}
        {emptyRows > 0 && (
          <TableRow style={{ height: 53 * emptyRows }}>
            <TableCell colSpan={headCells.length} />
          </TableRow>
        )}
      </>
    );
  }
  const table = (
    <>
      <TableContainer>
        <Box display='flex' justifyContent='space-between'>
          {title ? <EnhancedTableToolbar title={title} /> : null}
          <Box p={5} display='flex'>
            {actions || null}
          </Box>
        </Box>

        <Table
          className={classes.table}
          aria-labelledby='tableTitle'
          size='medium'
          aria-label='enhanced table'
        >
          <EnhancedTableHead<T>
            classes={classes}
            order={order}
            headCells={headCells}
            orderBy={orderBy}
            onRequestSort={handleRequestSort}
            rowCount={itemsCount}
            allowSort={allowSort}
          />
          <TableBody>{body}</TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={rowsPerPageOptions}
        component='div'
        count={itemsCount}
        rowsPerPage={rowsPerPage}
        page={page}
        onChangePage={handleChangePage}
        onChangeRowsPerPage={handleChangeRowsPerPage}
      />
    </>
  );

  return (
    <div className={classes.root}>
      {isOnPaper ? <Paper className={classes.paper}>{table}</Paper> : table}
    </div>
  );
}
