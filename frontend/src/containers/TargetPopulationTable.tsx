import React, { ReactElement, useState } from 'react';
import TableCell from '@material-ui/core/TableCell';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import {
  TargetPopulationNode, useAllTargetPopulationsQuery, AllTargetPopulationsQuery, AllTargetPopulationsQueryVariables, AllTargetPopulationsProps
} from '../__generated__/graphql';
import { Order, TableComponent } from '../components/table/TableComponent';
import { HeadCell } from '../components/table/EnhancedTableHead';
import { columnToOrderBy } from '../utils/utils';
import { useBusinessArea } from '../hooks/useBusinessArea';
import { ClickableTableRow } from '../components/table/ClickableTableRow';

const headCells: HeadCell<TargetPopulationNode>[] = [
  {
    disablePadding: false,
    label: 'Name',
    id: 'name',
    numeric: false,
  },
];
const StatusContainer = styled.div`
  width: 120px;
`;

export function TargetPopulationTable(): ReactElement {
  const history = useHistory();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const businessArea = useBusinessArea();
  const { data, fetchMore, loading } = useAllTargetPopulationsQuery({
    variables: {
      count: rowsPerPage,
    },
    fetchPolicy: 'network-only',
  });
  const handleClick = (row): void => {
    const path = `/${businessArea}/payment_records/${row.id}`;
    history.push(path);
  };
  if (!data) {
    return null;
  }
  const { edges } = data.allTargetPopulation;
  const population = edges.map((edge) => edge.node as TargetPopulationNode);
  return (
    <TableComponent<TargetPopulationNode>
      title='Target Population'
      data={population}
      loading={loading}
      renderRow={(row) => {
        return (
          <ClickableTableRow
            hover
            onClick={() => handleClick(row)}
            role='checkbox'
            key={row.id}
          >
            <TableCell align='left'>{row.name}</TableCell>
          </ClickableTableRow>
        );
      }}
      headCells={headCells}
      rowsPerPageOptions={[5, 10, 15]}
      rowsPerPage={rowsPerPage}
      page={page}
      itemsCount={data.allTargetPopulation.totalCount}
      handleChangePage={(event, newPage) => {
        let variables;
        if (newPage < page) {
          const before = edges[0].cursor;
          variables = {
            before,
            count: rowsPerPage,
          };
        } else {
          const after = edges[population.length - 1].cursor;
          variables = {
            after,
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
        const variables: AllTargetPopulationsQueryVariables = {
          count: rowsPerPage,
        };
        // if (orderBy) {
        //   variables.orderBy = columnToOrderBy(orderBy, orderDirection);
        // }
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
            count: rowsPerPage,
            //orderBy: columnToOrderBy(property, direction),
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
