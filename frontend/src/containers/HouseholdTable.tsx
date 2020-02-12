import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import { Order, TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';
import { HouseholdNode, useAllHouseholdsQuery } from '../__generated__/graphql';
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

interface HouseholdTableProps {
  sizeFilter: { min: number | undefined; max: number | undefined };
  textFilter: string;
  businessArea: string;
}

export const HouseholdTable = ({
  sizeFilter,
  textFilter,
  businessArea,
}: HouseholdTableProps): React.ReactElement => {
  const history = useHistory();

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');

  const { loading, data, fetchMore } = useAllHouseholdsQuery({
    variables: { first: rowsPerPage },
  });

  if (loading) return null;

  const handleClick = (row) => {
    const path = `/${businessArea}/population/household/${row.id}`;
    history.push(path);
  };

  if (sizeFilter.min || sizeFilter.max) {
    let variables;
    if (sizeFilter.min) {
      variables = { ...variables, familySizeGreater: sizeFilter.min };
    }
    if (sizeFilter.max) {
      variables = { ...variables, familySizeLower: sizeFilter.max };
    }
    fetchMore({
      variables,
      updateQuery: (prev, { fetchMoreResult }) => {
        return fetchMoreResult;
      },
    });
  }

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
        handleRequestSort={(e, property) => {
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
              first: rowsPerPage,
              // orderBy: columnToOrderBy(property, direction),
            },
            updateQuery: (prev, { fetchMoreResult }) => {
              return fetchMoreResult;
            },
          });
        }}
        renderRow={(row) => {
          return (
            <TableRow
              hover
              onClick={() => handleClick(row)}
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
              <TableCell align='right'>
                <Moment format='MM/DD/YYYY'>{row.createdAt}</Moment>
              </TableCell>
            </TableRow>
          );
        }}
        handleChangeRowsPerPage={(e) => {
          setRowsPerPage(Number(e.target.value));
        }}
        handleChangePage={(event, newPage) => {
          let variables;
          if (newPage < page) {
            const before = edges[0].cursor;
            variables = {
              before,
            };
          } else {
            const after = edges[result.length - 1].cursor;
            variables = {
              after,
            };
          }
          setPage(newPage);
          fetchMore({
            variables,
            updateQuery: (prev, { fetchMoreResult }) => {
              return fetchMoreResult;
            },
          });
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
