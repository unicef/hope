import React, { ReactElement, useState } from 'react';
import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import { HouseholdNode } from '../__generated__/graphql';
import { Order, TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';
import { ClickableTableRow } from '../components/table/ClickableTableRow';

const headCells: HeadCell<HouseholdNode>[] = [
  {
    disablePadding: false,
    label: 'Individual ID',
    id: 'individualId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Individual',
    id: 'individual',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Role',
    id: 'role',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Sex',
    id: 'sex',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Date of Birth',
    id: 'date_of_birth',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Employment / Education',
    id: 'employment',
    numeric: true,
  },
];
const StatusContainer = styled.div`
  width: 120px;
`;

interface HouseholdIndividualsTableProps {
  household: HouseholdNode;
}
export function HouseholdIndividualsTable({
  household,
}: HouseholdIndividualsTableProps): ReactElement {
  const history = useHistory();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const handleClick = (row): void => {};
  return (
    <TableComponent<HouseholdNode>
      title='Payment Records'
      data={[]}
      loading={false}
      renderRow={(row) => {
        return (
          <ClickableTableRow
            hover
            onClick={() => handleClick(row)}
            role='checkbox'
            key={row.id}
          >
            <TableCell align='left'></TableCell>
          </ClickableTableRow>
        );
      }}
      headCells={headCells}
      rowsPerPageOptions={[5, 10, 15]}
      rowsPerPage={rowsPerPage}
      page={page}
      itemsCount={0}
      handleChangePage={(event, newPage) => {}}
      handleChangeRowsPerPage={(event) => {}}
      handleRequestSort={(event, property) => {}}
      orderBy={orderBy}
      order={orderDirection as Order}
    />
  );
}
