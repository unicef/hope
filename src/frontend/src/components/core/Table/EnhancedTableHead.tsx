import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import styled from 'styled-components';
import TableSortLabel from '@mui/material/TableSortLabel';
import { Checkbox } from '@mui/material';
import { hasPermissions } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { MouseEvent, ReactElement } from 'react';

type Order = 'asc' | 'desc';

export interface HeadCell<T> {
  disablePadding: boolean;
  id: keyof T | string;
  label: string;
  numeric: boolean;
  weight?: number;
  dataCy?: string;
  disableSort?: boolean;
  requiredPermission?: string;
}

const VisuallyHidden = styled.span`
  border: 0;
  clip: rect(0 0 0 0);
  height: 1px;
  margin: -1px;
  overflow: hidden;
  padding: 0;
  position: absolute;
  top: 20px;
  width: 1px;
`;

const TableSortLabelStyled = styled(TableSortLabel)`
  & {
    font-size: 12px;
  }
`;

const StyledLabel = styled.span`
  font-size: 12px;
`;

interface EnhancedTableProps<T> {
  onRequestSort: (
    event: MouseEvent<unknown>,
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
): ReactElement {
  const {
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
  const createSortHandler =
    (property: keyof T | string) => (event: MouseEvent<unknown>) => {
      onRequestSort(event, property);
    };
  const permissions = usePermissions();
  return (
    <TableHead>
      <TableRow>
        {onSelectAllClick && data.length ? (
          <TableCell padding="checkbox">
            <Checkbox
              color="primary"
              indeterminate={numSelected > 0 && numSelected < rowCount}
              data-cy="checkbox-select-all"
              checked={rowCount > 0 && numSelected === rowCount}
              onChange={(event) => onSelectAllClick(event, data)}
              slotProps={{ input: { 'aria-label': 'select all' } }}
            />
          </TableCell>
        ) : null}
        {headCells.map((headCell) => {
          const canRenderCell =
            !headCell.requiredPermission ||
            hasPermissions(headCell.requiredPermission, permissions);
          return (
            canRenderCell && (
              <TableCell
                key={headCell.id.toString()}
                align={headCell.numeric ? 'right' : 'left'}
                padding={headCell.disablePadding ? 'none' : 'normal'}
                sortDirection={orderBy === headCell.id ? order : false}
                data-cy={headCell.dataCy}
              >
                {allowSort && !headCell.disableSort ? (
                  <TableSortLabelStyled
                    data-cy="table-label"
                    active={orderBy === headCell.id}
                    direction={orderBy === headCell.id ? order : 'asc'}
                    onClick={createSortHandler(headCell.id)}
                  >
                    {headCell.label}
                    {orderBy === headCell.id && (
                      <VisuallyHidden>
                        {order === 'desc'
                          ? 'sorted descending'
                          : 'sorted ascending'}
                      </VisuallyHidden>
                    )}
                  </TableSortLabelStyled>
                ) : (
                  <StyledLabel data-cy="table-label">
                    {headCell.label}
                  </StyledLabel>
                )}
              </TableCell>
            )
          );
        })}
      </TableRow>
    </TableHead>
  );
}
