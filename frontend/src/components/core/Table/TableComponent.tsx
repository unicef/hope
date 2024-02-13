import { KeyboardArrowLeft, KeyboardArrowRight } from '@mui/icons-material';
import FindInPageIcon from '@mui/icons-material/FindInPage';
import Skeleton from '@mui/lab/Skeleton';
import {
  IconButton,
  Box as MuiBox,
  Paper as MuiPaper,
  Table as MuiTable,
  TableBody as MuiTableBody,
  TableCell as MuiTableCell,
  TableContainer as MuiTableContainer,
  TableRow as MuiTableRow,
  TablePagination,
} from '@mui/material';
import { styled } from '@mui/system';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { v4 as uuidv4 } from 'uuid';
import { EnhancedTableHead, HeadCell } from './EnhancedTableHead';
import { EnhancedTableToolbar } from './EnhancedTableToolbar';

export type Order = 'asc' | 'desc';

const Root = styled('div')`
  width: 100%;
`;

const Paper = styled(MuiPaper)`
  width: 100%;
  margin-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

const Table = styled(MuiTable)`
  min-width: 750px;
`;

const Empty = styled('div')`
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: rgba(0, 0, 0, 0.38);
  font-size: 24px;
  line-height: 28px;
  text-align: center;
  padding: 70px;
`;

const SmallerText = styled(MuiBox)`
  font-size: 16px;
`;

const Icon = styled(FindInPageIcon)`
  font-size: 50px;
`;

const StyledTableRow = styled(MuiTableRow)`
  height: 70px;
  min-height: 70px;
`;

const StyledTableCell = styled(MuiTableCell)`
  col-span: ${(props) => props.colSpan};
`;

const EmptyMessage = styled('div')`
  ${Empty}
  ${Icon} {
    font-size: inherit;
  }
`;

const StyledTableContainer = styled(MuiTableContainer)``;

const StyledBox = styled(MuiBox)`
  display: flex;
  justify-content: space-between;
`;

const StyledTable = styled(Table)`
  aria-labelledby: 'tableTitle';
  size: 'medium';
  aria-label: 'enhanced table';
  data-cy: 'table-title';
`;

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

  function TablePaginationActions(props) {
    const { count, page, rowsPerPage, onPageChange } = props;

    const handleBackButtonClick = (event) => {
      onPageChange(event, page - 1);
    };

    const handleNextButtonClick = (event) => {
      onPageChange(event, page + 1);
    };

    return (
      <MuiBox sx={{ flexShrink: 0, ml: 2.5 }}>
        <IconButton
          onClick={handleBackButtonClick}
          disabled={page === 0 || loading}
          aria-label="previous page"
        >
          <KeyboardArrowLeft />
        </IconButton>
        <IconButton
          onClick={handleNextButtonClick}
          disabled={page >= Math.ceil(count / rowsPerPage) - 1 || loading}
          aria-label="next page"
        >
          <KeyboardArrowRight />
        </IconButton>
      </MuiBox>
    );
  }

  const emptyRows = itemsCount
    ? rowsPerPage - Math.min(rowsPerPage, itemsCount - page * rowsPerPage)
    : rowsPerPage;

  let body;

  if (loading) {
    body = Array.from({ length: rowsPerPage }).map(() => (
      <StyledTableRow key={uuidv4()} data-cy="table-row">
        <StyledTableCell colSpan={headCells.length}>
          <Skeleton variant="rectangular" width="100%" height={70} />
        </StyledTableCell>
      </StyledTableRow>
    ));
  } else if (!data?.length) {
    body = (
      <StyledTableRow data-cy="table-row" style={{ height: 70 * emptyRows }}>
        <StyledTableCell colSpan={headCells.length}>
          <EmptyMessage>
            <Icon fontSize="inherit" />
            <MuiBox mt={2}>No results</MuiBox>
            <SmallerText mt={2}>
              {t(
                'Try adjusting your search or your filters to find what you are looking for.',
              )}
            </SmallerText>
          </EmptyMessage>
        </StyledTableCell>
      </StyledTableRow>
    );
  } else {
    body = (
      <>
        {data.map((row) => renderRow(row))}
        {emptyRows > 0 && (
          <StyledTableRow style={{ height: 70 }}>
            <StyledTableCell colSpan={headCells.length} />
          </StyledTableRow>
        )}
      </>
    );
  }
  const table = (
    <>
      <StyledTableContainer>
        <StyledBox>
          {title ? <EnhancedTableToolbar title={title} /> : null}
          <StyledBox p={5}>{actions || null}</StyledBox>
        </StyledBox>

        <StyledTable>
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
          <MuiTableBody>{body}</MuiTableBody>
        </StyledTable>
      </StyledTableContainer>
      <TablePagination
        rowsPerPageOptions={rowsPerPageOptions}
        component="div"
        count={itemsCount}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        ActionsComponent={TablePaginationActions}
        data-cy="table-pagination"
      />
    </>
  );

  return <Root>{isOnPaper ? <Paper>{table}</Paper> : table}</Root>;
}
