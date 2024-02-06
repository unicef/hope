import { Box } from '@mui/material';
import { v4 as uuidv4 } from 'uuid';
import Paper from '@mui/material/Paper';
import Skeleton from '@mui/lab/Skeleton';
import { createStyles, makeStyles, Theme } from '@mui/material/styles';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import FindInPageIcon from '@mui/icons-material/FindInPage';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { EnhancedTableHead, HeadCell } from './EnhancedTableHead';
import { EnhancedTableToolbar } from './EnhancedTableToolbar';

export type Order = 'asc' | 'desc';

const useStyles = makeStyles((theme: Theme) => createStyles({
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
}));

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
  onSelectAllClick?: (event, rows) => void;
  numSelected?: number;
}

export function TableComponent<T>({
  title = '',
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
  loading = false,
  allowSort = true,
  isOnPaper = true,
  actions = [],
  onSelectAllClick,
  numSelected = 0,
}: TableComponentProps<T>): React.ReactElement {
  const { t } = useTranslation();
  const classes = useStyles({});

  const emptyRows = itemsCount
    ? rowsPerPage - Math.min(rowsPerPage, itemsCount - page * rowsPerPage)
    : rowsPerPage;
  let body;

  if (loading) {
    body = Array.from({ length: rowsPerPage }).map(() => (
      <TableRow
        key={uuidv4()}
        data-cy="table-row"
        style={{ height: 70, minHeight: 70 }}
      >
        <TableCell colSpan={headCells.length}>
          <Skeleton variant="rect" width="100%" height={70} />
        </TableCell>
      </TableRow>
    ));
  } else if (!data?.length) {
    body = (
      <TableRow
        data-cy="table-row"
        style={{ height: 70 * emptyRows, minHeight: 70 }}
      >
        <TableCell colSpan={headCells.length}>
          <div className={classes.empty}>
            <FindInPageIcon className={classes.icon} fontSize="inherit" />
            <Box mt={2}>No results</Box>
            <Box className={classes.smallerText} mt={2}>
              {t(
                'Try adjusting your search or your filters to find what you are looking for.',
              )}
            </Box>
          </div>
        </TableCell>
      </TableRow>
    );
  } else {
    body = (
      <>
        {data.map((row) => renderRow(row))}
        {emptyRows > 0 && (
          <TableRow style={{ height: 70 }}>
            <TableCell colSpan={headCells.length} />
          </TableRow>
        )}
      </>
    );
  }
  const table = (
    <>
      <TableContainer>
        <Box display="flex" justifyContent="space-between">
          {title ? <EnhancedTableToolbar title={title} /> : null}
          <Box p={5} display="flex">
            {actions || null}
          </Box>
        </Box>

        <Table
          className={classes.table}
          aria-labelledby="tableTitle"
          size="medium"
          aria-label="enhanced table"
          data-cy="table-title"
        >
          <EnhancedTableHead<T>
            order={order}
            headCells={headCells}
            orderBy={orderBy}
            onRequestSort={handleRequestSort}
            rowCount={data.length}
            allowSort={allowSort}
            onSelectAllClick={onSelectAllClick}
            data={data}
            numSelected={numSelected}
          />
          <TableBody>{body}</TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={rowsPerPageOptions}
        component="div"
        count={itemsCount}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        backIconButtonProps={{ ...(loading && { disabled: true }) }}
        nextIconButtonProps={{ ...(loading && { disabled: true }) }}
        data-cy="table-pagination"
      />
    </>
  );

  return (
    <div className={classes.root}>
      {isOnPaper ? <Paper className={classes.paper}>{table}</Paper> : table}
    </div>
  );
}
