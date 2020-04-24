import React, { ReactElement, useState } from 'react';
import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import { HouseholdNode, IndividualNode } from '../../__generated__/graphql';
import { Order, TableComponent } from '../../components/table/TableComponent';
import { HeadCell } from '../../components/table/EnhancedTableHead';
import { ClickableTableRow } from '../../components/table/ClickableTableRow';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { StatusBox } from '../../components/StatusBox';
import {
  decodeIdString,
  paymentRecordStatusToColor,
  sexToCapitalize,
} from '../../utils/utils';
import { Missing } from '../../components/Missing';

const headCells: HeadCell<IndividualNode>[] = [
  {
    disablePadding: false,
    label: 'Individual ID',
    id: 'individualCaId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Individual',
    id: 'fullName',
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
    label: 'Employment / Education',
    id: 'workStatus',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Date of Birth',
    id: 'birthDate',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Sex',
    id: 'sex',
    numeric: false,
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
  const businessArea = useBusinessArea();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const handleClick = (row): void => {
    history.push(`/${businessArea}/population/individuals/${row.id}`);
  };

  const allIndividuals = household.individuals.edges.map((edge) => edge.node);

  if (orderBy) {
    if (orderDirection === 'asc') {
      allIndividuals.sort((a, b) => {
        return a[orderBy] < b[orderBy] ? 1 : -1;
      });
    } else {
      allIndividuals.sort((a, b) => {
        return a[orderBy] > b[orderBy] ? 1 : -1;
      });
    }
  }

  const totalCount = allIndividuals.length;
  return (
    <TableComponent<IndividualNode>
      title='Individuals in Household'
      data={allIndividuals.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage,
      )}
      allowSort={false}
      renderRow={(row) => {
        return (
          <ClickableTableRow
            hover
            onClick={() => handleClick(row)}
            role='checkbox'
            key={row.id}
          >
            <TableCell align='left'>{decodeIdString(row.id)}</TableCell>
            <TableCell align='left'>{row.fullName}</TableCell>
            <TableCell align='left'>
              <StatusContainer>
                <StatusBox
                  status='no data'
                  statusToColor={paymentRecordStatusToColor}
                />
              </StatusContainer>
            </TableCell>
            <TableCell align='left'>{row.relationship}</TableCell>
            <TableCell align='left'>
              <Missing />
            </TableCell>
            <TableCell align='right'>
              {row.birthDate ? 'N/A' : row.birthDate}
            </TableCell>
            <TableCell align='left'>{sexToCapitalize(row.sex)}</TableCell>
          </ClickableTableRow>
        );
      }}
      headCells={headCells}
      rowsPerPageOptions={totalCount < 5 ? [totalCount] : [5, 10, 15]}
      rowsPerPage={totalCount > 5 ? rowsPerPage : totalCount}
      page={page}
      itemsCount={totalCount}
      handleChangePage={(event, newPage) => {
        setPage(newPage);
      }}
      handleChangeRowsPerPage={(event) => {
        setRowsPerPage(Number(event.target.value));
        setPage(0);
      }}
      handleRequestSort={(event, property) => {
        let direction = 'asc';
        if (property === orderBy) {
          direction = orderDirection === 'asc' ? 'desc' : 'asc';
        }
        setOrderBy(property);
        setOrderDirection(direction);
      }}
      orderBy={orderBy}
      order={orderDirection as Order}
    />
  );
}
