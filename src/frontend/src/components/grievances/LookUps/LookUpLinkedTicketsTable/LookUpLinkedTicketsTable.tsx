import * as React from 'react';
import { useState } from 'react';
import { UniversalTable } from '@containers/tables/UniversalTable';
import { choicesToDict, dateToIsoString } from '@utils/utils';
import {
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  useAllGrievanceTicketQuery,
  useGrievancesChoiceDataQuery,
} from '@generated/graphql';
import { TableWrapper } from '@core/TableWrapper';
import { headCells } from './LookUpLinkedTicketsHeadCells';
import { LookUpLinkedTicketsTableRow } from './LookUpLinkedTicketsTableRow';

interface LookUpLinkedTicketsTableProps {
  businessArea: string;
  filter;
  setFieldValue;
  initialValues;
}

export function LookUpLinkedTicketsTable({
  businessArea,
  filter,
  setFieldValue,
  initialValues,
}: LookUpLinkedTicketsTableProps): React.ReactElement {
  const { data: choicesData, loading: choicesLoading } =
    useGrievancesChoiceDataQuery();
  const initialVariables: AllGrievanceTicketQueryVariables = {
    businessArea,
    search: filter.search.trim(),
    documentType: choicesData?.documentTypeChoices?.[0]?.value,
    documentNumber: filter.documentNumber.trim(),
    status: [filter.status],
    fsp: filter.fsp,
    createdAtRange: JSON.stringify({
      min: dateToIsoString(filter.createdAtRangeMin, 'startOfDay'),
      max: dateToIsoString(filter.createdAtRangeMax, 'endOfDay'),
    }),
    admin2: filter?.admin2?.node?.id,
  };
  const [selected, setSelected] = useState(initialValues.selectedLinkedTickets);
  if (choicesLoading) {
    return null;
  }
  const statusChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketStatusChoices);

  const categoryChoices: {
    [id: number]: string;
  } = choicesToDict(choicesData.grievanceTicketCategoryChoices);

  const handleCheckboxClick = (
    _event:
    | React.MouseEvent<HTMLButtonElement, MouseEvent>
    | React.MouseEvent<HTMLTableRowElement, MouseEvent>,
    name: string,
  ): void => {
    const selectedIndex = selected.indexOf(name);
    const newSelected = [...selected];

    if (selectedIndex === -1) {
      newSelected.push(name);
    } else {
      newSelected.splice(selectedIndex, 1);
    }
    setSelected(newSelected);
    setFieldValue('selectedLinkedTickets', newSelected);
  };

  const handleSelectAllCheckboxesClick = (_event, rows): void => {
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
        queriedObjectName="allGrievanceTicket"
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
}
