import React, { useState } from 'react';
import { UniversalTable } from '../../../../containers/tables/UniversalTable';
import { decodeIdString, choicesToDict } from '../../../../utils/utils';
import {
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  useAllGrievanceTicketQuery,
  useGrievancesChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { TableWrapper } from '../../../core/TableWrapper';
import { headCells } from './LookUpLinkedTicketsHeadCells';
import { LookUpLinkedTicketsTableRow } from './LookUpLinkedTicketsTableRow';

interface LookUpLinkedTicketsTableProps {
  businessArea: string;
  filter;
  setFieldValue;
  initialValues;
}

export const LookUpLinkedTicketsTable = ({
  businessArea,
  filter,
  setFieldValue,
  initialValues,
}: LookUpLinkedTicketsTableProps): React.ReactElement => {
  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
    search: filter.search,
    status: [filter.status],
    fsp: filter.fsp,
    createdAtRange: JSON.stringify(filter.createdAtRange),
    admin: [decodeIdString(filter?.admin?.node?.id)],
  };
  const [selected, setSelected] = useState(initialValues.selectedLinkedTickets);
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();
  if (choicesLoading) {
    return null;
  }
  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketCategoryChoices);

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
    setFieldValue('selectedLinkedTickets', newSelected);
  };

  const handleSelectAllCheckboxesClick = (event, rows): void => {
    if (!selected.length) {
      const newSelecteds = rows.map((row) => row.id);
      setSelected(newSelecteds);
      setFieldValue('selectedLinkedTickets', newSelecteds);

      return;
    }
    setSelected([]);
    setFieldValue('selectedLinkedTickets', []);
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
          <LookUpLinkedTicketsTableRow
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
