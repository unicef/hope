import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import Moment from 'react-moment';
import { HouseholdNode, useAllHouseholdsQuery } from '../../__generated__/graphql';
import { columnToOrderBy } from '../../utils/utils';
import { Order, TableComponent } from '../../components/table/TableComponent';
import { HeadCell } from '../../components/table/EnhancedTableHead';

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

const formatCurrency = (amount: number): string =>
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
  businessArea,
}: HouseholdTableProps): React.ReactElement => {
  const history = useHistory();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const [after, setAfter] = useState();
  const [before, setBefore] = useState();
  const [first, setFirst] = useState(rowsPerPage);
  const [last, setLast] = useState(rowsPerPage);

  const { loading, data, refetch } = useAllHouseholdsQuery({
    variables: {
      first,
      last,
      after,
      before,
      businessArea,
      familySizeGreater: Number(sizeFilter.min),
      familySizeLower: Number(sizeFilter.max),
      orderBy,
    },
  });

  const handleClick = (row: HouseholdNode): void => {
    const path = `/${businessArea}/population/household/${row.id}`;
    history.push(path);
  };

  useEffect(() => {
    refetch();
  }, [refetch]);

  if (loading) return null;

  const { edges, pageInfo } = data.allHouseholds;
  const houseHolds = edges.map((edge) => edge.node as HouseholdNode);

  return (
    <TableWrapper>
      <TableComponent<HouseholdNode>
        loading={loading}
        title='Households'
        page={page}
        data={houseHolds}
        itemsCount={data.allHouseholds.totalCount}
        handleRequestSort={(e, property) => {
          let direction = 'asc';
          if (property === orderBy) {
            direction = orderDirection === 'asc' ? 'desc' : 'asc';
          }
          setOrderBy(property);
          setOrderDirection(direction);
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
          setPage(0);
          setRowsPerPage(Number(e.target.value));
          setAfter(null);
          setFirst(rowsPerPage);
          setLast(null);
          setBefore(null);
        }}
        handleChangePage={(event, newPage) => {
          if (newPage === 0) {
            setFirst(rowsPerPage);
            setLast(null);
            setAfter(null);
            setBefore(null);
          } else if (newPage === data.allHouseholds.totalCount / rowsPerPage) {
            setLast(rowsPerPage);
            setFirst(null);
            setAfter(null);
            setBefore(null);
          } else if (newPage > page) {
            setAfter(pageInfo.endCursor);
            setFirst(rowsPerPage);
            setBefore(null);
            setLast(null);
          } else {
            setBefore(pageInfo.startCursor);
            setLast(rowsPerPage);
            setAfter(null);
            setFirst(null);
          }
          if (orderBy) {
            setOrderBy(columnToOrderBy(orderBy, orderDirection));
          }
          setPage(newPage);
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
