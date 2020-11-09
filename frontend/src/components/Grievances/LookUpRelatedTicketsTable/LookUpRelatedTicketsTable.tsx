import React, { useState } from 'react';
import styled from 'styled-components';
import { UniversalTable } from '../../../containers/tables/UniversalTable';
import { reduceChoices } from '../../../utils/utils';
import {
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  useAllGrievanceTicketQuery,
  useGrievancesChoiceDataQuery,
} from '../../../__generated__/graphql';
import { headCells } from './LookUpRelatedTicketsHeadCells';
import { LookUpRelatedTicketsTableRow } from './LookUpRelatedTicketsTableRow';

const TableWrapper = styled.div`
  padding: 20px;
`;

interface LookUpRelatedTicketsTableProps {
  businessArea: string;
  filter;
  setFieldValue;
  initialValues;
}

export const LookUpRelatedTicketsTable = ({
  businessArea,
  filter,
  setFieldValue,
  initialValues,
}: LookUpRelatedTicketsTableProps): React.ReactElement => {
  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
    search: filter.search,
    status: [filter.status],
    fsp: [filter.fsp],
    createdAtRange: JSON.stringify(filter.createdAtRange),
    admin: [filter.admin],
  };
  const [selected, setSelected] = useState(
    initialValues.selectedRelatedTickets,
  );
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();
  if (choicesLoading) {
    return null;
  }
  const statusChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = reduceChoices(choicesData.grievanceTicketCategoryChoices);

  const handleCheckboxClick = (event, name): void => {
    const selectedIndex = selected.indexOf(name);
    let newSelected = [];

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, name);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1),
      );
    }

    setSelected(newSelected);
    setFieldValue('selectedRelatedTickets', newSelected);
  };

  const handleSelectAllCheckboxesClick = (event, rows): void => {
    if (event.target.checked) {
      const newSelecteds = rows.map((row) => row.id);
      setSelected(newSelecteds);
      setFieldValue('selectedRelatedTickets', newSelecteds);

      return;
    }
    setSelected([]);
    setFieldValue('selectedRelatedTickets', []);
  };
  const numSelected = selected.length;

  return (
    <TableWrapper>
      <UniversalTable<
        AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
        AllGrievanceTicketQueryVariables
      >
        headCells={headCells}
        rowsPerPageOptions={[10, 15, 20]}
        query={useAllGrievanceTicketQuery}
        queriedObjectName='allGrievanceTicket'
        initialVariables={initialVariables}
        onSelectAllClick={handleSelectAllCheckboxesClick}
        numSelected={numSelected}
        renderRow={(row) => (
          <LookUpRelatedTicketsTableRow
            key={row.id}
            ticket={row}
            statusChoices={statusChoices}
            categoryChoices={categoryChoices}
            checkboxClickHandler={handleCheckboxClick}
            selected={selected}
          />
        )}
      />
    </TableWrapper>
  );
};
