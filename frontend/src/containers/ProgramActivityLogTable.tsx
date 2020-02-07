import React, { ReactElement, useState } from 'react';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import {
  AllCashPlansQueryVariables,
  CashPlanNode,
  LogEntryAction,
  LogEntryObject,
  ProgramNode,
  useAllLogEntriesQuery,
} from '../__generated__/graphql';
import { Order, TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';
import { columnToOrderBy } from '../utils/utils';
import { useBusinessArea } from '../hooks/useBusinessArea';
import moment from 'moment';

const headCells: HeadCell<CashPlanNode>[] = [
  {
    disablePadding: false,
    label: 'Date',
    id: 'timestamp',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'User',
    id: 'actor',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Action',
    id: 'action',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Change from',
    id: 'change_from',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Change to',
    id: 'change_to',
    numeric: false,
  },
];
const StatusContainer = styled.div`
  width: 120px;
`;

interface ProgramActivityLogTableProps {
  program: ProgramNode;
}
export function ProgramActivityLogTable({
  program,
}: ProgramActivityLogTableProps): ReactElement {
  const history = useHistory();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const businessArea = useBusinessArea();
  const { data, fetchMore } = useAllLogEntriesQuery({
    variables: {
      objectId: program.id,
      count: rowsPerPage,
    },
    fetchPolicy: 'network-only',
  });
  const handleClick = (row) => {
    const path = `/${businessArea}/cashplans/${row.id}`;
    history.push(path);
  };
  if (!data) {
    return null;
  }
  const { edges } = data.allLogEntries;
  const cashPlans = edges.map((edge) => edge.node as LogEntryObject);
  return (
    <TableComponent<LogEntryObject>
      title='Activity Log'
      data={cashPlans}
      renderRow={(row) => {
        const changes =[];
        return (
          <TableRow
            hover
            onClick={() => handleClick(row)}
            role='checkbox'
            key={row.id}
          >
            <TableCell align='left'>
              {moment(row.timestamp).format('DD MMM YYYY')}
            </TableCell>
            <TableCell align='right'>
              {row.actor
                ? `${row.actor.firstName} ${row.actor.lastName}`
                : null}
            </TableCell>
            <TableCell align='left'>
              {row.action === LogEntryAction.A_1 ? 'Update' : 'Create'}
            </TableCell>
            <TableCell colSpan={2}>
              {}
            </TableCell>
          </TableRow>
        );
      }}
      headCells={headCells}
      rowsPerPageOptions={[5, 10, 15]}
      rowsPerPage={rowsPerPage}
      page={page}
      itemsCount={data.allLogEntries.totalCount}
      handleChangePage={(event, newPage) => {
        let variables;
        if (newPage < page) {
          const before = edges[0].cursor;
          variables = {
            before,
            program: program.id,
            count: rowsPerPage,
          };
        } else {
          const after = edges[cashPlans.length - 1].cursor;
          variables = {
            after,
            program: program.id,
            count: rowsPerPage,
          };
        }
        if (orderBy) {
          variables.orderBy = columnToOrderBy(orderBy, orderDirection);
        }
        setPage(newPage);
        fetchMore({
          variables,
          updateQuery: (prev, { fetchMoreResult }) => {
            return fetchMoreResult;
          },
        });
      }}
      handleChangeRowsPerPage={(event) => {
        const value = parseInt(event.target.value, 10);
        setRowsPerPage(value);
        setPage(0);
        const variables: AllCashPlansQueryVariables = {
          program: program.id,
          count: value,
        };
        if (orderBy) {
          variables.orderBy = columnToOrderBy(orderBy, orderDirection);
        }
        fetchMore({
          variables,
          updateQuery: (prev, { fetchMoreResult }) => {
            return fetchMoreResult;
          },
        });
      }}
      handleRequestSort={(event, property) => {
        let direction = 'asc';
        if (property === orderBy) {
          direction = orderDirection === 'asc' ? 'desc' : 'asc';
        }
        setOrderBy(property);
        setOrderDirection(direction);
        if (edges.length < 0) {
          return;
        }

        fetchMore({
          variables: {
            program: program.id,
            count: rowsPerPage,
            orderBy: columnToOrderBy(property, direction),
          },
          updateQuery: (prev, { fetchMoreResult }) => {
            return fetchMoreResult;
          },
        });
      }}
      orderBy={orderBy}
      order={orderDirection as Order}
    />
  );
}
