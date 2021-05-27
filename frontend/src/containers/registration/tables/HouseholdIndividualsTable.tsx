import React, {ReactElement, useState} from 'react';
import styled from 'styled-components';
import {useHistory} from 'react-router-dom';
import {ImportedIndividualMinimalFragment, useHouseholdChoiceDataQuery} from '../../../__generated__/graphql';
import {LoadingComponent} from '../../../components/LoadingComponent';
import {HeadCell} from "../../../components/table/EnhancedTableHead";
import {useBusinessArea} from "../../../hooks/useBusinessArea";
import {Order, TableComponent} from "../../../components/table/TableComponent";
import {ImportedIndividualsTableRow} from './ImportedIndividualsTable/ImportedIndividualsTableRow';

const headCells: HeadCell<ImportedIndividualMinimalFragment>[] = [
  {
    disablePadding: false,
    label: 'Individual ID',
    id: 'unicefId',
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
    label: 'Role',
    id: 'role',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Relationship to HoH',
    id: 'relationship',
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
    label: 'Gender',
    id: 'sex',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Dedupe within Batch',
    id: 'deduplicationBatchStatus',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Dedupe against Population',
    id: 'deduplicationGoldenRecordStatus',
    numeric: false,
  },
];
const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

export function HouseholdImportedIndividualsTable({
  household,
}): ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');

  const { data: choicesData, loading } = useHouseholdChoiceDataQuery();

  if (loading) return <LoadingComponent />;

  if (!choicesData) {
    return null;
  }

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
    <TableComponent<ImportedIndividualMinimalFragment>
      title='Individuals in Household'
      data={allIndividuals.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage,
      )}
      allowSort={false}
      renderRow={(row) => {
        return (
          <ImportedIndividualsTableRow choices={choicesData} individual={row} />
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
