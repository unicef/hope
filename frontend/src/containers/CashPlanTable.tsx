import React, { ReactElement, useState } from 'react';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import Moment from 'react-moment';
import { useHistory } from 'react-router-dom';
import {
  AllCashPlansQueryVariables,
  CashPlanNode,
  ProgramNode,
  useAllCashPlansQuery,
} from '../__generated__/graphql';
import { Order, TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';
import { StatusBox } from '../components/StatusBox';
import { cashPlanStatusToColor, columnToOrderBy } from '../utils/utils';

const headCells: HeadCell<CashPlanNode>[] = [
  {
    disablePadding: false,
    label: 'Cash Plan ID',
    id: 'cashAssistId',
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
    label: 'No. of Households',
    id: 'numberOfHouseholds',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Currency',
    id: 'currency',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Total Entitled Quantity',
    id: 'totalEntitledQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Delivered Quantity',
    id: 'totalDeliveredQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Undelivered Quantity',
    id: 'totalUndeliveredQuantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Dispersion Date',
    id: 'dispersionDate',
    numeric: false,
  },
];
const StatusContainer = styled.div`
  width: 120px;
`;

interface CashPlanTableProps {
  program: ProgramNode;
}
export function CashPlanTable({ program }: CashPlanTableProps): ReactElement {
  const history = useHistory();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const { data, fetchMore } = useAllCashPlansQuery({
    variables: {
      program: program.id,
      count: rowsPerPage,
    },
    fetchPolicy: 'network-only',
  });
  const handleClick = (row) => {
    history.push(`/cashplans/${row.id}`);
  };
  if (!data) {
    return null;
  }
  const { edges } = data.allCashPlans;
  const cashPlans = edges.map((edge) => edge.node as CashPlanNode);
  return (
    <TableComponent<CashPlanNode>
      title='Cash Plans'
      data={cashPlans}
      renderRow={(row) => {
        return (
          <TableRow
            hover
            onClick={() => handleClick(row)}
            role='checkbox'
            key={row.id}
          >
            <TableCell align='left'>{row.cashAssistId}</TableCell>
            <TableCell align='left'>
              <StatusContainer>
                <StatusBox
                  status={row.status}
                  statusToColor={cashPlanStatusToColor}
                />
              </StatusContainer>
            </TableCell>
            <TableCell align='right'>{row.numberOfHouseholds}</TableCell>
            <TableCell align='left'>{row.currency}</TableCell>
            <TableCell align='right'>
              {row.totalEntitledQuantity.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </TableCell>
            <TableCell align='right'>
              {row.totalDeliveredQuantity.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </TableCell>
            <TableCell align='right'>
              {row.totalUndeliveredQuantity.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </TableCell>
            <TableCell align='left'>
              <Moment format='MM/DD/YYYY'>{row.dispersionDate}</Moment>
            </TableCell>
          </TableRow>
        );
      }}
      headCells={headCells}
      rowsPerPageOptions={[5, 10, 15]}
      rowsPerPage={rowsPerPage}
      page={page}
      itemsCount={data.allCashPlans.totalCount}
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
