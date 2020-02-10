import React, { ReactElement, useState } from 'react';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import Moment from 'react-moment';
import {
  AllPaymentRecordsQueryVariables,
  CashPlanNode,
  PaymentRecordNode,
  useAllPaymentRecordsQuery,
} from '../__generated__/graphql';
import { Order, TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';
import { StatusBox } from '../components/StatusBox';
import { columnToOrderBy, paymentRecordStatusToColor } from '../utils/utils';
import { useBusinessArea } from '../hooks/useBusinessArea';
import { Link } from '../components/Link';

const headCells: HeadCell<PaymentRecordNode>[] = [
  {
    disablePadding: false,
    label: 'Payment ID',
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
    label: 'Head of Household',
    id: 'headOfHousehold',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'household__household_ca_id',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'totalPersonCovered',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Entitlement',
    id: 'entitlement__entitlement_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Delivered Amount',
    id: 'entitlement__delivered_quantity',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Delivery Date',
    id: 'entitlement__delivery_date',
    numeric: true,
  },
];
const StatusContainer = styled.div`
  width: 120px;
`;
interface CashPlanTableProps {
  cashPlan: CashPlanNode;
}
export function PaymentRecordTable({
  cashPlan,
}: CashPlanTableProps): ReactElement {
  const history = useHistory();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const businessArea = useBusinessArea();
  const { data, fetchMore, loading } = useAllPaymentRecordsQuery({
    variables: {
      cashPlan: cashPlan.id,
      count: rowsPerPage,
    },
    fetchPolicy: 'network-only',
  });
  const handleClick = (row) => {
    const path = `/${businessArea}/payment_records/${row.id}`;
    history.push(path);
  };
  if (!data) {
    return null;
  }
  const { edges } = data.allPaymentRecords;
  const paymentRecords = edges.map((edge) => edge.node as PaymentRecordNode);
  return (
    <TableComponent<PaymentRecordNode>
      title='Payment Records'
      data={paymentRecords}
      loading={loading}
      renderRow={(row) => {
        return (
          <TableRow
            hover
            component={Link}
            // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
            // @ts-ignore
            to={`/${businessArea}/payment_records/${row.id}`}
            key={row.id}
          >
            <TableCell align='left'>{row.cashAssistId}</TableCell>
            <TableCell align='left'>
              <StatusContainer>
                <StatusBox
                  status={row.status}
                  statusToColor={paymentRecordStatusToColor}
                />
              </StatusContainer>
            </TableCell>
            <TableCell align='left'>{row.headOfHousehold}</TableCell>
            <TableCell align='left'>{row.household.householdCaId}</TableCell>
            <TableCell align='left'>{row.totalPersonCovered}</TableCell>
            <TableCell align='right'>
              {row.entitlement.entitlementQuantity.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </TableCell>
            <TableCell align='right'>
              {row.entitlement.deliveredQuantity.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </TableCell>
            <TableCell align='right'>
              <Moment format='MM/DD/YYYY'>
                {row.entitlement.deliveryDate}
              </Moment>
            </TableCell>
          </TableRow>
        );
      }}
      headCells={headCells}
      rowsPerPageOptions={[5, 10, 15]}
      rowsPerPage={rowsPerPage}
      page={page}
      itemsCount={data.allPaymentRecords.totalCount}
      handleChangePage={(event, newPage) => {
        let variables;
        if (newPage < page) {
          const before = edges[0].cursor;
          variables = {
            before,
            cashPlan: cashPlan.id,
            count: rowsPerPage,
          };
        } else {
          const after = edges[paymentRecords.length - 1].cursor;
          variables = {
            after,
            cashPlan: cashPlan.id,
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
            console.log('fetchMoreResult');
            return fetchMoreResult;
          },
        });
      }}
      handleChangeRowsPerPage={(event) => {
        const value = parseInt(event.target.value, 10);
        setRowsPerPage(value);
        setPage(0);
        const variables: AllPaymentRecordsQueryVariables = {
          cashPlan: cashPlan.id,
          count: rowsPerPage,
        };
        if (orderBy) {
          variables.orderBy = columnToOrderBy(orderBy, orderDirection);
        }
        fetchMore({
          variables,
          updateQuery: (prev, { fetchMoreResult }) => {
            console.log('fetchMoreResult');
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
            cashPlan: cashPlan.id,
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
