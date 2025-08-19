import {
  EnhancedTableHead,
  HeadCell,
} from '@components/core/Table/EnhancedTableHead';
import { EnhancedTableToolbar } from '@components/core/Table/EnhancedTableToolbar';
import FindInPageIcon from '@mui/icons-material/FindInPage';
import {
  Box as MuiBox,
  Paper as MuiPaper,
  Table as MuiTable,
  TableBody as MuiTableBody,
  TableCell as MuiTableCell,
  TableContainer as MuiTableContainer,
  TableRow as MuiTableRow,
  Skeleton,
  TablePagination,
} from '@mui/material';
import TablePaginationActions from '@mui/material/TablePagination/TablePaginationActions';
import { ReactElement, ChangeEvent, MouseEvent } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

export type Order = 'asc' | 'desc';

const Root = styled('div')`
  width: 100%;
`;

const Paper = styled(MuiPaper)`
  width: 100%;
  margin-bottom: 8px;
  overflow: clip;
`;

const Table = styled(MuiTable)`
  min-width: 750px;
`;

const StyledTableRow = styled(MuiTableRow)`
  height: 70px;
  min-height: 70px;
`;

const StyledTableCell = styled(MuiTableCell)`
  col-span: ${(props) => props.colSpan};

  && {
    white-space: nowrap;
    overflow: auto;
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

const EmptyMessage = styled.div`
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #a9a9a9;
  font-size: 24px;
  line-height: 28px;
  text-align: center;
  padding: 70px;
`;

const SmallerText = styled(MuiBox)`
  font-size: 16px;
  color: #a9a9a9;
`;

const IconContainer = styled(MuiBox)`
  font-size: 50px;
`;

const Icon = styled(FindInPageIcon)`
  & svg {
    color: #9e9e9e;
  }
`;

interface TableRestComponentProps<T extends { [key: string]: any }> {
  data: T[];
  renderRow: (row: T) => ReactElement;
  headCells: HeadCell<T>[];
  rowsPerPageOptions: number[];
  rowsPerPage: number;
  page: number;
  itemsCount: number;
  handleChangePage: (event: unknown, newPage: number) => void;
  handleChangeRowsPerPage: (event: ChangeEvent<HTMLInputElement>) => void;
  handleRequestSort: (event: MouseEvent<unknown>, property: string) => void;
  orderBy: string;
  order: Order;
  title?: string;
  loading?: boolean;
  allowSort?: boolean;
  isOnPaper?: boolean;
  actions?: Array<ReactElement>;
  onSelectAllClick?: (event: ChangeEvent<HTMLInputElement>, rows: T[]) => void;
  numSelected?: number;
  hidePagination?: boolean;
}

export function TableRestComponent<T>({
  title = '',
  renderRow,
  data,
  headCells,
  rowsPerPageOptions,
  rowsPerPage,
  page,
  itemsCount,
  handleChangePage: handleChangePageProp,
  handleChangeRowsPerPage,
  handleRequestSort,
  order,
  orderBy,
  onSelectAllClick,
  loading: loadingProp = false,
  allowSort = true,
  isOnPaper = true,
  actions = [],
  numSelected = 0,
  hidePagination = false,
}: TableRestComponentProps<T>): ReactElement {
  const { t } = useTranslation();

  const emptyRows =
    rowsPerPage - Math.min(rowsPerPage, itemsCount - page * rowsPerPage);

  let body;

  if (loadingProp) {
    body = Array.from({ length: rowsPerPage }).map((_, index) => (
      <StyledTableRow key={index} data-cy="table-row">
        <StyledTableCell colSpan={headCells.length}>
          <Skeleton variant="rectangular" width="100%" height={70} />
        </StyledTableCell>
      </StyledTableRow>
    ));
  } else if (!data.length) {
    body = (
      <StyledTableRow data-cy="table-row" style={{ height: 70 * emptyRows }}>
        <StyledTableCell colSpan={headCells.length}>
          <EmptyMessage>
            <IconContainer>
              <Icon fontSize="inherit" />
            </IconContainer>
            <MuiBox mt={2}>{t('No results')}</MuiBox>
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
          <StyledTableRow style={{ height: 70 * emptyRows }}>
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
      {!hidePagination && (
        <TablePagination
          rowsPerPageOptions={rowsPerPageOptions}
          component="div"
          count={
            itemsCount == null || itemsCount === undefined ? -1 : itemsCount
          }
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePageProp}
          onRowsPerPageChange={handleChangeRowsPerPage}
          ActionsComponent={TablePaginationActions}
          data-cy="table-pagination"
        />
      )}
    </>
  );

  return <Root>{isOnPaper ? <Paper>{table}</Paper> : table}</Root>;
}
