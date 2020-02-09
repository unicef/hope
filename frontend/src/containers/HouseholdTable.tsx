import React, { useState } from 'react';
import styled from 'styled-components';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import { Order, TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';
import { HouseholdNode } from '../__generated__/graphql';
import { useQuery } from '@apollo/react-hooks';
import { AllHouseholds } from '../apollo/queries/AllHouseholds';
import Moment from 'react-moment';

const headCells: HeadCell<HouseholdNode>[] = [
  {
    disablePadding: false,
    label: 'Household ID',
    id: 'householdCaId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Head of Household',
    id: 'paymentRecords',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Household Size',
    id: 'familySize',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Location',
    id: 'location',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Residence Status',
    id: 'residenceStatus',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Total Cash Received',
    id: 'paymentRecords',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Registration Date',
    id: 'createdAt',
    numeric: true,
  },
];

const TableWrapper = styled.div`
  padding: 20px;
`;

const formatCurrency = (amount: number) =>
  amount.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });

export const HouseholdTable = (): React.ReactElement => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');

  const { loading, data } = useQuery(AllHouseholds, { variables: { id } });
  if (loading) return null;

  console.log(data);
  const { edges } = data.allHouseholds;
  const houseHolds = edges.map((edge) => edge.node as HouseholdNode);
  const result = houseHolds.filter(
    (x: HouseholdNode) => x.paymentRecords.edges.length,
  );

  return (
    <TableWrapper>
      <TableComponent<HouseholdNode>
        title='Households'
        page={page}
        data={result}
        itemsCount={data.allHouseholds.totalCount}
        handleRequestSort={(e) => {
          console.log(e);
        }}
        renderRow={(row) => {
          return (
            <TableRow
              hover
              // onClick={(event) => handleClick(event, row.)}
              role='checkbox'
              key={row.id}
            >
              <TableCell align='left'>{row.householdCaId}</TableCell>
              <TableCell align='left'>
                {row.paymentRecords.edges[0].node.headOfHousehold}
              </TableCell>
              <TableCell align='right'>{row.familySize}</TableCell>
              <TableCell align='left'>{row.location.title}</TableCell>
              <TableCell align='right'>{row.residenceStatus}</TableCell>
              <TableCell align='right'>
                {formatCurrency(
                  row.paymentRecords.edges[0].node.cashPlan
                    .totalDeliveredQuantity,
                )}
              </TableCell>
              <TableCell align='left'>
                <Moment format='MM/DD/YYYY'>{row.createdAt}</Moment>
              </TableCell>
            </TableRow>
          );
        }}
        handleChangeRowsPerPage={(e) => {
          console.log(e);
        }}
        handleChangePage={(e) => {
          console.log(e);
        }}
        headCells={headCells}
        rowsPerPageOptions={[5, 10, 15]}
        rowsPerPage={rowsPerPage}
        orderBy={orderBy}
        order={orderDirection as Order}
      />
    </TableWrapper>
  );
};
