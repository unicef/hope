import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import Moment from 'react-moment';
import {
  useAllIndividualsQuery,
  IndividualNode,
} from '../__generated__/graphql';
import { columnToOrderBy } from '../utils/utils';
import { Order, TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';

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
    label: 'Household ID',
    id: 'householdCaId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Age',
    id: 'age',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Sex',
    id: 'sex',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Location',
    id: 'location',
    numeric: false,
  },
];

const TableWrapper = styled.div`
  padding: 20px;
`;

interface IndividualsListTableProps {
  ageFilter: { min: number | undefined; max: number | undefined };
  textFilter?: string;
  businessArea?: string;
}

export const IndividualsListTable = ({
  ageFilter,
  businessArea,
}: IndividualsListTableProps): React.ReactElement => {
  const history = useHistory();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const [after, setAfter] = useState();
  const [before, setBefore] = useState();
  const [first, setFirst] = useState(rowsPerPage);
  const [last, setLast] = useState(rowsPerPage);

  const { loading, data, refetch } = useAllIndividualsQuery({
    variables: {
      first,
      last,
      after,
      before,
      //   ageGreater: ageFilter.min,
      //   ageLower: ageFilter.max
    },
  });

  const handleClick = (row: IndividualNode): void => {
    const path = `/${businessArea}/population/individuals/${row.id}`;
    history.push(path);
  };

  useEffect(() => {
    refetch();
  }, [refetch]);

  if (loading) return null;

  const { edges, pageInfo } = data.allIndividuals;
  const individuals = edges.map((edge) => edge.node as IndividualNode);

  return (
    <TableWrapper>
      <TableComponent<IndividualNode>
        loading={loading}
        title='Households'
        page={page}
        data={individuals}
        itemsCount={data.allIndividuals.totalCount}
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
              <TableCell align='left'>{row.individualCaId}</TableCell>
              <TableCell align='left'>{row.fullName}</TableCell>
              <TableCell align='left'>{row.household.householdCaId}</TableCell>
              <TableCell align='left'>{row.dob}</TableCell>
              <TableCell align='right'>{row.sex}</TableCell>
              <TableCell align='right'>
                {row.household.location.title}
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
          } else if (newPage === data.allIndividuals.totalCount / rowsPerPage) {
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
